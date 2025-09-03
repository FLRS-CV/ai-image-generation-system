import './globals.css';
export const metadata = {
	title: "Virtual Staging",
	description: "Generate virtual staging via ComfyUI backend",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="en">
			<head>
				<link rel="preconnect" href="https://fonts.googleapis.com" />
				<link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
				<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
			</head>
			<body className="container">
				{children}
			</body>
		</html>
	);
}
