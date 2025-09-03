'use client';
// indicates client-side component (runs in browser, not server)
import { useState, useEffect } from 'react'; // useState(manages component state), useEffect (runs code when component mounts or state changes)
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';

export default function HomePage() {
	const [imageFile, setImageFile] = useState<File | null>(null);
	const [prompt, setPrompt] = useState('A modern minimal living room, clean design, photorealistic');
	const [negativePrompt, setNegativePrompt] = useState('lowres, blurry, distorted, cartoonish');
	const [ckptName, setCkptName] = useState('juggernaut_reborn.safetensors');
	const [seed, setSeed] = useState('');
	const [loading, setLoading] = useState(false);
	const [results, setResults] = useState<{ image: string; file_url?: string; seed?: number }[]>([]);
	const [error, setError] = useState<string | null>(null);
	const [numImages, setNumImages] = useState(1);
	const [apiKey, setApiKey] = useState('');
	const [apiKeyValid, setApiKeyValid] = useState<boolean | null>(null);
	const [validating, setValidating] = useState(false);
	const [quotaInfo, setQuotaInfo] = useState<{ remaining?: number; total?: number } | null>(null);
	const backendUrl = '/api/generate'; // Use our Next.js API route instead of direct Flask

	// Load API key from localStorage on component mount
	useEffect(() => {
		const savedApiKey = localStorage.getItem('virtual-staging-api-key');
		if (savedApiKey) {
			setApiKey(savedApiKey);
			validateAPIKeyDebounced(savedApiKey);
		}
	}, []);

	// Save API key to localStorage when it changes
	useEffect(() => {
		if (apiKey) {
			localStorage.setItem('virtual-staging-api-key', apiKey);
		} else {
			localStorage.removeItem('virtual-staging-api-key');
		}
	}, [apiKey]);

	// Debounced API key validation
	useEffect(() => {
		if (!apiKey.trim()) {
			setApiKeyValid(null);
			setQuotaInfo(null);
			return;
		}
		
		const timeoutId = setTimeout(() => {
			validateAPIKeyDebounced(apiKey);
		}, 500);

		return () => clearTimeout(timeoutId);
	}, [apiKey]);

	const validateAPIKeyDebounced = async (key: string) => {
		if (!key.trim()) return;
		// validating with api - key - manager
		setValidating(true);
		try {
			const response = await fetch('http://localhost:8004/api/keys/validate', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ api_key: key }),
			});

			if (response.ok) {
				const data = await response.json();
				if (data.valid) {
					setApiKeyValid(true);
					setQuotaInfo({
						remaining: data.key_info?.daily_quota - data.key_info?.current_daily_usage,
						total: data.key_info?.daily_quota
					});
				} else {
					setApiKeyValid(false);
					setQuotaInfo(null);
				}
			} else {
				setApiKeyValid(false);
				setQuotaInfo(null);
			}
		} catch (error) {
			console.error('API key validation error:', error);
			setApiKeyValid(false);
			setQuotaInfo(null);
		} finally {
			setValidating(false);
		}
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);
		setResults([]);
		
		// Validate inputs
		if (!imageFile) {
			setError('Please upload an image.');
			return;
		}
		
		if (!apiKey.trim()) {
			setError('Please provide a valid API key.');
			return;
		}
		
		// form being send to middleware then backend (comfy)
		setLoading(true);
		try {
			const form = new FormData();
			form.append('image_file', imageFile);
			form.append('prompt_text', prompt);
			form.append('negative_prompt_text', negativePrompt);
			form.append('ckpt_name', ckptName); 
			form.append('num_images', String(numImages));
			if (seed) form.append('seed', seed);
			form.append('workflow', 'joger.json');

			// Include API key in headers
			// validation with middleware before generating images
			const res = await fetch(backendUrl, { 
				method: 'POST', 
				body: form,
				headers: {
					'x-api-key': apiKey
				}
			});
			// catch error from middleware 401, 403 and others
			if (!res.ok) {
				const data = await res.json().catch(() => ({}));
				throw new Error((data as any).error || `Request failed: ${res.status}`);
			}
			
			const data = (await res.json()) as {
				results?: { image: string; file_url?: string; seed?: number }[];
				error?: string;
				user_info?: { email?: string; quota_remaining?: string };
			};
			// if got successfull response from comfy
			if (data.results && data.results.length > 0) {
				setResults(data.results);
				setApiKeyValid(true);
				
				// Update quota info if available
				if (data.user_info?.quota_remaining) {
					setQuotaInfo({ remaining: parseInt(data.user_info.quota_remaining) });
				}
			} else {
				setError(data.error || 'No images returned');
			}
		} catch (err: any) {
			setError(err.message || 'Unknown error');
			
			// If it's an API key error, mark as invalid
			if (err.message?.includes('API key') || err.message?.includes('Invalid') || err.message?.includes('401') || err.message?.includes('403')) {
				setApiKeyValid(false);
			}
		} finally {
			setLoading(false);
		}
	};

	return (
		<div>
			<div className="header">
				<div>
					<div className="title">Deco_Core</div>
					<div className="subtitle">Proof of Concept</div>
				</div>
			</div>

			{/* API Key Section - Always at the top */}
			<div className="grid">
				<div className="card">
					<div className="section-title">🔐 API Key Authentication</div>
					<div className="form">
						<label className="label">
							<span>Enter your API key to access the image generation features</span>
							<input
								className={`input ${apiKeyValid === false ? 'error-input' : apiKeyValid === true ? 'success-input' : ''}`}
								type="password"
								value={apiKey}
								onChange={(e) => setApiKey(e.target.value)}
								placeholder="sk-proj-..."
							/>
							{validating && <div className="field-info">🔄 Validating API key...</div>}
							{apiKeyValid === false && <div className="field-error">❌ Invalid API key</div>}
							{apiKeyValid === true && (
								<div className="field-success">
									✅ Valid API key! Quota remaining: {quotaInfo?.remaining || 'Unknown'}/{quotaInfo?.total || 'Unknown'}
								</div>
							)}
						</label>
					</div>
				</div>
			</div>

			{/* Main Interface - Only show if API key is valid */}
			{apiKeyValid === true && (
				<div className="grid">
					<div className="card">
						<div className="section-title">📸 Image Generation</div>
						<form className="form" onSubmit={handleSubmit}>
							<label className="label">
								<span>Upload image</span>
								<input
									className="file"
									type="file"
									accept="image/*"
									onChange={(e) => setImageFile(e.target.files?.[0] || null)}
								/>
							</label>
							<label className="label">
								<span>Positive prompt</span>
								<textarea className="textarea" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
							</label>
							<label className="label">
								<span>Negative prompt</span>
								<textarea
									className="textarea"
									value={negativePrompt}
									onChange={(e) => setNegativePrompt(e.target.value)}
								/>
							</label>
							<div className="row">
								<label className="label">
									<span>Checkpoint</span>
									<input className="input" value={ckptName} onChange={(e) => setCkptName(e.target.value)} />
								</label>
								<label className="label">
									<span>Seed (optional)</span>
									<input
										className="input"
										value={seed}
										onChange={(e) => setSeed(e.target.value)}
										placeholder="e.g. 123456"
									/>
								</label>
							</div>
							<label className="label">
								<span>Number of Images</span>
								<input
									className="input"
									type="number"
									min={1}
									max={10}
									value={numImages}
									onChange={(e) => setNumImages(Number(e.target.value))}
								/>
							</label>
							<button className="button" type="submit" disabled={loading}>
								{loading ? 'Generating…' : 'Generate'}
							</button>
							{error && <div className="error">{error}</div>}
						</form>
					</div>

					<div className="card preview">
						<div className="section-title">Output</div>
						{results.map((r, i) => (
							<div key={i} className="output-item">
								{/* Comparison slider */}
								{imageFile && (
									<ReactCompareSlider
										itemOne={<ReactCompareSliderImage src={URL.createObjectURL(imageFile)} alt="Original" />}
										itemTwo={<ReactCompareSliderImage src={r.image} alt={`Generated ${i + 1}`} />}
									/>
								)}

								<div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
									<a className="button" href={r.image} download={`virtual_staging_${i + 1}.png`}>
										Download
									</a>
									{r.file_url && (
										<a className="link" href={r.file_url} target="_blank" rel="noreferrer">
											Open saved file
										</a>
									)}
								</div>
								{r.seed !== undefined && <div className="helper">Seed: {r.seed}</div>}
							</div>
						))}
					</div>
				</div>
			)}

			{/* Show message when API key is not valid */}
			{apiKeyValid === false && (
				<div className="grid">
					<div className="card">
						<div className="section-title">🚫 Access Denied</div>
						<p>Please enter a valid API key to access the image generation features.</p>
						<p>You can generate an API key at: <a href="http://localhost:8004" target="_blank" rel="noreferrer">http://localhost:8004</a></p>
					</div>
				</div>
			)}
		</div>
	);
}
