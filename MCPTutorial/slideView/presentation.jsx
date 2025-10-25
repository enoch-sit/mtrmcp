const { useState, useEffect, useRef } = React;

// Lucide icons as inline SVG components
const ChevronLeft = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
    </svg>
);

const ChevronRight = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
);

const Code = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="16 18 22 12 16 6"></polyline>
        <polyline points="8 6 2 12 8 18"></polyline>
    </svg>
);

const Diagram = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="9" y1="3" x2="9" y2="21"></line>
        <line x1="15" y1="3" x2="15" y2="21"></line>
        <line x1="3" y1="9" x2="21" y2="9"></line>
        <line x1="3" y1="15" x2="21" y2="15"></line>
    </svg>
);

function Presentation() {
    const [currentSlide, setCurrentSlide] = useState(0);
    const [showCode, setShowCode] = useState(true);
    const [showDiagram, setShowDiagram] = useState(true);
    const mermaidRef = useRef(null);

    useEffect(() => {
        const handleKeyPress = (e) => {
            if (e.key === 'ArrowRight' && currentSlide < slidesData.length - 1) {
                setCurrentSlide(prev => prev + 1);
            } else if (e.key === 'ArrowLeft' && currentSlide > 0) {
                setCurrentSlide(prev => prev - 1);
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [currentSlide]);

    useEffect(() => {
        // Re-render Mermaid diagrams when slide changes
        if (mermaidRef.current && currentSlideData.mermaid) {
            mermaid.contentLoaded();
        }
    }, [currentSlide, showDiagram]);

    const nextSlide = () => {
        setCurrentSlide((prev) => Math.min(prev + 1, slidesData.length - 1));
    };

    const prevSlide = () => {
        setCurrentSlide((prev) => Math.max(prev - 1, 0));
    };

    const goToSlide = (index) => {
        setCurrentSlide(index);
    };

    const currentSlideData = slidesData[currentSlide];
    const hasCode = currentSlideData.code !== null && currentSlideData.code !== undefined;
    const hasMermaid = currentSlideData.mermaid !== null && currentSlideData.mermaid !== undefined;

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
            <div className="w-full max-w-7xl bg-white rounded-2xl shadow-2xl overflow-hidden">
                {/* Slide Content */}
                <div className="p-10 slide-content">
                    <div className="mb-6 flex items-center justify-between">
                        <span className="text-sm font-semibold text-purple-600 uppercase tracking-wide">
                            Slide {currentSlide + 1} of {slidesData.length}
                        </span>
                        <div className="flex gap-2">
                            {hasCode && (
                                <button
                                    onClick={() => setShowCode(!showCode)}
                                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium"
                                >
                                    <Code />
                                    {showCode ? 'Hide Code' : 'Show Code'}
                                </button>
                            )}
                            {hasMermaid && (
                                <button
                                    onClick={() => setShowDiagram(!showDiagram)}
                                    className="flex items-center gap-2 px-4 py-2 bg-purple-100 hover:bg-purple-200 rounded-lg transition-colors text-sm font-medium"
                                >
                                    <Diagram />
                                    {showDiagram ? 'Hide Diagram' : 'Show Diagram'}
                                </button>
                            )}
                        </div>
                    </div>
                    
                    <h1 className="text-4xl font-bold text-gray-900 mb-8">
                        {currentSlideData.title}
                    </h1>
                    
                    <div className="space-y-6">
                        {/* Bullets Section */}
                        <div>
                            <ul className="space-y-4">
                                {currentSlideData.bullets.map((bullet, index) => (
                                    <li key={index} className="flex items-start gap-3">
                                        <span className="flex-shrink-0 w-2 h-2 bg-purple-600 rounded-full mt-2"></span>
                                        <span className="text-lg text-gray-700 leading-relaxed">{bullet}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Mermaid Diagram */}
                        {hasMermaid && showDiagram && (
                            <div className="bg-gray-50 rounded-lg p-6 overflow-auto">
                                <div 
                                    ref={mermaidRef}
                                    className="mermaid-diagram mermaid"
                                    dangerouslySetInnerHTML={{ __html: currentSlideData.mermaid }}
                                />
                            </div>
                        )}
                        
                        {/* Code Section */}
                        {hasCode && showCode && (
                            <div className="bg-gray-900 rounded-lg p-6 overflow-auto max-h-[400px]">
                                <pre className="text-sm text-gray-100 overflow-x-auto">
                                    <code>{currentSlideData.code}</code>
                                </pre>
                            </div>
                        )}
                    </div>
                </div>

                {/* Navigation */}
                <div className="bg-gray-50 px-12 py-6 flex items-center justify-between border-t border-gray-200">
                    <button
                        onClick={prevSlide}
                        className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={currentSlide === 0}
                    >
                        <ChevronLeft />
                        Previous
                    </button>

                    {/* Slide Indicators */}
                    <div className="flex gap-2 overflow-x-auto max-w-md">
                        {slidesData.map((_, index) => (
                            <button
                                key={index}
                                onClick={() => goToSlide(index)}
                                className={`flex-shrink-0 w-3 h-3 rounded-full transition-all ${
                                    index === currentSlide
                                        ? 'bg-purple-600 w-8'
                                        : 'bg-gray-300 hover:bg-gray-400'
                                }`}
                                aria-label={`Go to slide ${index + 1}`}
                            />
                        ))}
                    </div>

                    <button
                        onClick={nextSlide}
                        className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={currentSlide === slidesData.length - 1}
                    >
                        Next
                        <ChevronRight />
                    </button>
                </div>
            </div>

            {/* Keyboard Hint */}
            <div className="mt-6 text-sm text-gray-600">
                Use arrow keys ← → to navigate
            </div>
        </div>
    );
}

ReactDOM.render(<Presentation />, document.getElementById('root'));
