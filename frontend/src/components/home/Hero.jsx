import React from 'react';
import { Link } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const Hero = () => {
    const { isAuthenticated } = useAuthStore();

    return (
        <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-900">
            {/* Background Image with Overlay */}
            <div className="absolute inset-0 z-0">
                <img
                    src="/assets/hero-bg.png"
                    alt="AI Network Background"
                    className="w-full h-full object-cover opacity-30"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-slate-900/50 via-slate-900/80 to-slate-900"></div>
            </div>

            {/* Star Animations */}
            <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
                {[...Array(20)].map((_, i) => (
                    <div
                        key={i}
                        className="star animate-star-glow"
                        style={{
                            top: `${Math.random() * 100}%`,
                            left: `${Math.random() * 100}%`,
                            width: `${Math.random() * 3 + 1}px`,
                            height: `${Math.random() * 3 + 1}px`,
                            animationDelay: `${Math.random() * 4}s`,
                            animationDuration: `${Math.random() * 3 + 3}s`
                        }}
                    ></div>
                ))}
            </div>

            {/* Content */}
            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center h-full flex flex-col justify-center">
                <div className="animate-fade-in-up">
                    <span className="inline-block py-1 px-3 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-semibold mb-6 backdrop-blur-sm">
                        Powered by Advanced AI
                    </span>

                    <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
                        Unlock Your <br />
                        <span className="gradient-text">Career Potential</span>
                    </h1>

                    <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
                        Optimize your resume with our intelligent ATS scorer and find the perfect job matches tailored to your unique skills profile.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        {isAuthenticated ? (
                            <>
                                <Link to="/analyzer" className="btn-primary group">
                                    <span className="relative z-10 flex items-center gap-2">
                                        Analyze Resume
                                        <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                        </svg>
                                    </span>
                                </Link>
                                <Link to="/jobs" className="btn-secondary flex items-center gap-2">
                                    Explore Jobs
                                </Link>
                            </>
                        ) : (
                            <>
                                <Link to="/signup" className="btn-primary group">
                                    <span className="relative z-10 flex items-center gap-2">
                                        Get Started Free
                                        <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                        </svg>
                                    </span>
                                </Link>
                                <Link to="/login" className="btn-secondary flex items-center gap-2">
                                    Sign In
                                </Link>
                            </>
                        )}
                    </div>
                </div>


            </div>

            {/* Scroll Down Indicator */}
            <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce text-slate-400">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
            </div>
        </div>
    );
};

export default Hero;
