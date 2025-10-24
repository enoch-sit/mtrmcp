const { useState, useEffect } = React;

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

function Presentation() {
    const [currentSlide, setCurrentSlide] = useState(0);
    const [showCode, setShowCode] = useState(true);

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
    const hasImage = currentSlideData.image !== undefined;

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
            <div className="w-full max-w-6xl bg-white rounded-2xl shadow-2xl overflow-hidden">
                {/* Slide Content */}
                <div className="p-12 min-h-96">
                    <div className="mb-6 flex items-center justify-between">
                        <span className="text-sm font-semibold text-indigo-600 uppercase tracking-wide">
                            Slide {currentSlide + 1} of {slidesData.length}
                        </span>
                        {hasCode && (
                            <button
                                onClick={() => setShowCode(!showCode)}
                                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium"
                            >
                                <Code />
                                {showCode ? 'Hide Code' : 'Show Code'}
                            </button>
                        )}
                    </div>
                    
                    <h1 className="text-4xl font-bold text-gray-900 mb-8">
                        {currentSlideData.title}
                    </h1>
                    
                    <div className={`grid ${hasCode && showCode ? 'grid-cols-2' : 'grid-cols-1'} gap-8`}>
                        <div>
                            <ul className="space-y-4">
                                {currentSlideData.bullets.map((bullet, index) => (
                                    <li key={index} className="flex items-start gap-3">
                                        <span className="flex-shrink-0 w-2 h-2 bg-indigo-600 rounded-full mt-2"></span>
                                        <span className="text-lg text-gray-700 leading-relaxed">{bullet}</span>
                                    </li>
                                ))}
                            </ul>
                            
                            {hasImage && (
                                <div className="mt-6">
                                    <img 
                                        src={currentSlideData.image} 
                                        alt={currentSlideData.title}
                                        className="slide-image"
                                    />
                                </div>
                            )}
                        </div>
                        
                        {hasCode && showCode && (
                            <div className="bg-gray-900 rounded-lg p-6 overflow-auto max-h-[500px]">
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
                        className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
                                        ? 'bg-indigo-600 w-8'
                                        : 'bg-gray-300 hover:bg-gray-400'
                                }`}
                                aria-label={`Go to slide ${index + 1}`}
                            />
                        ))}
                    </div>

                    <button
                        onClick={nextSlide}
                        className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
