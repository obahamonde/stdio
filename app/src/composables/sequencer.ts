import { Data } from './../../../.venv/lib/python3.10/site-packages/gradio/_frontend_code/dataframe/shared/utils';


type AudioSample = {
	audio: Float32Array;
	sample_rate: number;
	duration: number;
	time: number;
	url?: string;
	key?: string;
}

type AudioPrompt = {
	text: string;
	audio?: Float32Array;
}

export const useSequencer = () => {
	const audioContext = new AudioContext();
	const state = reactive({
		samples: [] as AudioSample[],
		loading: 0
	});

	let analyser: AnalyserNode | null = null;

	const canvas = ref<HTMLCanvasElement | null>(null);

	const generateMusic = async (prompt: AudioPrompt) => {
		const timeout = setInterval(() => {
			state.loading += 1;
		}, 1000);

		const { data } = await useFetch("/api/music/default", {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(prompt)
		}).json<AudioSample>();

		const sample = unref(data);
		if (sample) {
			playAudio(sample.audio, sample.sample_rate);
			state.samples.push(sample);
			clearInterval(timeout);
			state.loading = 0;
		}
	}

	const playAudio = (audio: Float32Array, sample_rate: number) => {
		if (!analyser) {
			analyser = audioContext.createAnalyser();
			analyser.fftSize = 2048;
			analyser.connect(audioContext.destination);
			drawFrequencyData();
		}
		const audioBuffer = audioContext.createBuffer(1, audio.length, sample_rate);
		audioBuffer.getChannelData(0).set(audio);
		const source = audioContext.createBufferSource();
		source.buffer = audioBuffer;
		source.connect(analyser);
		source.start();
	}

	const playAllSequentially = () => {
		let accumulatedDelay = 0;
		state.samples.forEach((sample, index) => {
			setTimeout(() => {
				playAudio(sample.audio, sample.sample_rate);
			}, accumulatedDelay);
			accumulatedDelay += sample.duration * 1000;
		});
	};

	const drawFrequencyData = () => {
		if (!analyser || !canvas.value) return;

		const canvasContext = canvas.value!.getContext('2d');
		const frequencyData = new Uint8Array(analyser.frequencyBinCount);
		analyser.getByteFrequencyData(frequencyData);
		canvasContext!.clearRect(0, 0, canvas.value.width, canvas.value.height);
		for (let i = 0; i < frequencyData.length; i++) {
			const value = frequencyData[i];
			const percent = value / 256;
			const height = canvas.value.height * percent;
			const offset = canvas.value.height - height - 1;
			const barWidth = canvas.value.width / frequencyData.length;
			canvasContext!.fillStyle = 'hsl(' + (i / frequencyData.length) * 360 + ', 100%, 50%)';
			canvasContext!.fillRect(i * barWidth, offset, barWidth, height);
		}

		requestAnimationFrame(drawFrequencyData);
	};

	const presignedUrl = () => {
		const { data } = useEventSource('/api/music/default');
		watch(data, (newData) => {
			if (newData) {
				const json = JSON.parse(newData);
				const url = json.url;
				const key = json.key;
				let obj = state.samples[state.samples.length - 1];
				if (obj)
					Object.assign(obj, { url, key });
			}
		}
		);
	}
	return {
		generateMusic,
		state,
		playAudio,
		playAllSequentially,
		drawFrequencyData,
		canvas,
		presignedUrl
	}

}

