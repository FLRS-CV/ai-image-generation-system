'use client';

import { useState, useEffect } from 'react';
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
	const [quotaInfo, setQuotaInfo] = useState<{ remaining?: number; total?: number } | null>(null);
	const backendUrl = '/api/generate'; // Use our Next.js API route instead of direct Flask

	// Load API key from localStorage on component mount
	useEffect(() => {
		const savedApiKey = localStorage.getItem('virtual-staging-api-key');
		if (savedApiKey) {
			setApiKey(savedApiKey);
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

	// Function to validate API key in real-time
	const validateAPIKey = async (key: string) => {
		if (!key.trim()) {
			setApiKeyValid(null);
			setQuotaInfo(null);
			return;
		}

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
				setApiKeyValid(data.valid);
				if (data.valid && data.remaining_quota !== undefined) {
					setQuotaInfo({ remaining: data.remaining_quota });
				}
			} else {
				setApiKeyValid(false);
				setQuotaInfo(null);
			}
		} catch (error) {
			console.error('Error validating API key:', error);
			setApiKeyValid(false);
			setQuotaInfo(null);
		}
	};

	// Validate API key when it changes (with debounce)
	useEffect(() => {
		const timeoutId = setTimeout(() => {
			if (apiKey) {
				validateAPIKey(apiKey);
			}
		}, 500); // 500ms debounce

		return () => clearTimeout(timeoutId);
	}, [apiKey]);

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
			const res = await fetch(backendUrl, { 
				method: 'POST', 
				body: form,
				headers: {
					'x-api-key': apiKey
				}
			});
			
			if (!res.ok) {
				const data = await res.json().catch(() => ({}));
				throw new Error((data as any).error || `Request failed: ${res.status}`);
			}
			
			const data = (await res.json()) as {
				results?: { image: string; file_url?: string; seed?: number }[];
				error?: string;
				user_info?: { email?: string; quota_remaining?: string };
			};
			
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
			
			{/* API Key Validation Section - Always Visible */}
			<div className="card" style={{ marginBottom: '24px' }}>
				<div className="section-title">API Key Authentication</div>
				<div className="form">
					<label className="label">
						<span>API Key</span>
						<input
							className={`input ${apiKeyValid === false ? 'error-input' : apiKeyValid === true ? 'success-input' : ''}`}
							type="password"
							value={apiKey}
							onChange={(e) => setApiKey(e.target.value)}
							placeholder="sk-proj-..."
						/>
						{apiKeyValid === false && <div className="field-error">Invalid API key</div>}
						{apiKeyValid === true && quotaInfo && (
							<div className="field-success">
								✅ Valid API key. Quota remaining: {quotaInfo.remaining || 'Unknown'}
							</div>
						)}
						{apiKeyValid === null && (
							<div className="helper">
								Enter your API key to access image generation features. 
								Get one from <a href="http://localhost:8004" target="_blank" className="link">API Key Manager</a>.
							</div>
						)}
					</label>
				</div>
			</div>

			{/* Image Generation Inputs - Only Visible When API Key is Valid */}
			{apiKeyValid === true && (
				<div className="grid">
					<div className="card">
						<div className="section-title">Image Generation</div>
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
		</div>
	);
}
