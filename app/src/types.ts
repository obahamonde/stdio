type AudioSample = {
	audio: Float32Array;
	sample_rate: number;
	duration: number;
	time: number;
	url: string;
	key: string;
};

type AudioPrompt = {
	text?: string;
	audio?: Float32Array;
};