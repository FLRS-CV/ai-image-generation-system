module.exports = {
	reactStrictMode: true,
	images: {
		remotePatterns: [
			{ protocol: 'http', hostname: '**' },
			{ protocol: 'https', hostname: '**' },
		],
	},
};
