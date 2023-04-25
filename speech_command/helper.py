import os
import random
import pathlib
import numpy as np
import tensorflow as tf


AUTOTUNE = tf.data.AUTOTUNE

class speech_command():
    def __init__(self) -> None:
        self.budget = 0
        self.passed = 0
        self.exceptions = 0
        self.num_dupl_bugs   = 0
        self.precond_violtn  = 0
        self.postcond_violtn = 0
        self.label_dict      = {}

        self.bug_inps = set()
        self.cur_rand = ()
        self.rand_dict = {}

    def setSeed(self, seed):
        random.seed(seed)

    def get_label_text(self, file_path):
        parts = tf.strings.split(
            input=file_path,
            sep=os.path.sep)
        # Note: You'll use indexing here instead of tuple unpacking to enable this
        # to work in a TensorFlow graph.
        return parts[-2]


    def decode_audio(self, audio_binary):
        # Decode WAV-encoded audio files to `float32` tensors, normalized
        # to the [-1.0, 1.0] range. Return `float32` audio and a sample rate.
        audio, _ = tf.audio.decode_wav(contents=audio_binary)
        # Since all the data is single channel (mono), drop the `channels`
        # axis from the array.
        return tf.squeeze(audio, axis=-1)


    def get_waveform_and_label(self, file_path):
        label = self.get_label_text(file_path)
        audio_binary = tf.io.read_file(file_path)
        waveform = self.decode_audio(audio_binary)
        return waveform, label


    def get_spectrogram(self, waveform):
        # Zero-padding for an audio waveform with less than 16,000 samples.
        input_len = 16000
        waveform = waveform[:input_len]
        zero_padding = tf.zeros(
            [16000] - tf.shape(waveform),
            dtype=tf.float32)
        # Cast the waveform tensors' dtype to float32.
        waveform = tf.cast(waveform, dtype=tf.float32)
        # Concatenate the waveform with `zero_padding`, which ensures all audio
        # clips are of the same length.
        equal_length = tf.concat([waveform, zero_padding], 0)
        # Convert the waveform to a spectrogram via a STFT.
        spectrogram = tf.signal.stft(
            equal_length, frame_length=255, frame_step=128)
        # Obtain the magnitude of the STFT.
        spectrogram = tf.abs(spectrogram)
        # Add a `channels` dimension, so that the spectrogram can be used
        # as image-like input data with convolution layers (which expect
        # shape (`batch_size`, `height`, `width`, `channels`).
        spectrogram = spectrogram[..., tf.newaxis]
        return spectrogram


    def get_spectrogram_and_label_id(self, audio, label):
        spectrogram = self.get_spectrogram(audio)
        commands = ['right', 'go', 'no', 'left', 'stop', 'up', 'down', 'yes']
        label_id = tf.argmax(label == commands)
        return spectrogram, label_id


    def preprocess_waves(self, files):
        files_ds = tf.data.Dataset.from_tensor_slices(files)
        output_ds = files_ds.map(
            map_func=self.get_waveform_and_label,
            num_parallel_calls=AUTOTUNE)
        return output_ds


    def preprocess_spectrogram(self, output_ds):
        output_ds = output_ds.map(
            map_func=self.get_spectrogram_and_label_id,
            num_parallel_calls=AUTOTUNE)
        return output_ds


    def preprocess_dataset(self, files):
        files_ds = tf.data.Dataset.from_tensor_slices(files)
        output_ds = files_ds.map(
            map_func=self.get_waveform_and_label,
            num_parallel_calls=AUTOTUNE)
        output_ds = output_ds.map(
            map_func=self.get_spectrogram_and_label_id,
            num_parallel_calls=AUTOTUNE)
        return output_ds

    
    def load(self, model_path):
        self.model = tf.keras.models.load_model(model_path)  # "speech_command/model")

        data_dir = pathlib.Path("speech_command/mini_speech_commands")
        if not data_dir.exists():
            tf.keras.utils.get_file(
                'mini_speech_commands.zip',
                origin="http://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip",
                extract=True,
                cache_dir='.', cache_subdir='.'
            )

        filenames = tf.io.gfile.glob(str(data_dir) + '/*/*')
        filenames.sort()  # needed for reproducability
        # filenames = tf.
        random.shuffle(filenames)
        filenames = filenames[6400:]  # use only test set

        wave_outs = self.preprocess_waves(filenames)
        inputs = self.preprocess_spectrogram(wave_outs)

        inp_audio = []
        labels = []
        for inp, lbl in inputs:
            inp_audio.append(inp.numpy())
            labels.append(lbl.numpy())

        # inp_audio = np.array(inp_audio)

        # y_pred = np.argmax(model.predict(inp_audio), axis=1)
        # y_true = inp_labels

        # test_acc = sum(y_pred == y_true) / len(y_true)
        # print(f'Test set accuracy: {test_acc:.0%}')

        self.inputs = inp_audio
        self.labels = np.array(labels)


    def randInput(self):
        r = random.randint(0, len(self.inputs)-1)
        self.cur_rand += r,
        inp, lbl = self.inputs[r], self.labels[r]
        inp = np.expand_dims(inp, axis=0)
        self.label_dict[str(inp)] = lbl
        return inp       

    def randInt(self, l, u):
        r = random.randint(l, u)
        self.cur_rand += r,
        return r

    def label(self, x):
        lbl = self.label_dict[str(x)]
        lbl = np.argmax(lbl)
        return lbl

    def wNoise(self, wave, max_noise=0.05):
        r = random.randint(0, 2**32-1)
        self.cur_rand += r,
        np.random.seed(r)
        noise = np.random.normal(0, max_noise, wave.shape)
        noisy_wave = wave + noise

        return noisy_wave

    def predict(self, x):
        d = self.model.predict(x)
        d = np.argmax(d, axis=1)[0]
        return d
        
    def process_bug(self):
        if self.cur_rand and self.cur_rand in self.rand_dict:
            self.num_dupl_bugs += 1
        else:
            self.rand_dict[self.cur_rand] = True

        self.bug_inps.add(self.cur_rand[0])
