import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

const CTA = () => {
    return (
        <section className="py-24 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-900/50 to-purple-900/50 z-0"></div>

            <div className="max-w-4xl mx-auto px-4 relative z-10 text-center">
                <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
                    Ready to accelerate your career?
                </h2>
                <p className="text-xl text-slate-300 mb-10">
                    Join thousands of job seekers who have optimized their resumes and found their dream jobs with our AI-powered platform.
                </p>

                <Link to="/analyzer" className="btn-primary inline-flex items-center gap-2 transform hover:scale-105 transition-transform text-lg px-10 py-4">
                    Get Started for Free
                    <ArrowRight className="w-5 h-5" />
                </Link>
            </div>
        </section>
    );
};

export default CTA;
