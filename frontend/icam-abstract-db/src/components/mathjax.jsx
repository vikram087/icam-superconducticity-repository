import { MathJax, MathJaxContext } from "better-react-mathjax";

function Content({ content }) {
	const config = {
		loader: { load: ["[tex]/html"] },
		tex: {
			packages: { "[+]": ["html"] },
			inlineMath: [
				["$", "$"],
				["\\(", "\\)"],
			],
			displayMath: [
				["$$", "$$"],
				["\\[", "\\]"],
			],
		},
	};

	return (
		<MathJaxContext version={3} config={config}>
			<MathJax hideUntilTypeset={"first"}>{`${content}`}</MathJax>
		</MathJaxContext>
	);
}

export default Content;
