import React from 'react';
import { CheckCircle2 } from 'lucide-react';

const benefits = [
    "Identify keywords missing from your resume",
    "Instant feedback on formatting and structure",
    "Compare your profile against top job descriptions",
    "Discover alternative job titles you match for",
    "Track your application potential score",
    "Get specific skill improvement recommendations"
];

const HowItHelps = () => {
    return (
        <section className="py-24 bg-slate-900 overflow-hidden">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col lg:flex-row items-center gap-16">

                    <div className="lg:w-1/2 animate-float">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl blur-2xl opacity-20"></div>
                            <div className="relative bg-slate-800/80 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
                                <div className="space-y-4">
                                    <div className="h-4 bg-slate-700/50 rounded w-3/4"></div>
                                    <div className="h-4 bg-slate-700/30 rounded w-full"></div>
                                    <div className="h-4 bg-slate-700/30 rounded w-5/6"></div>
                                    <div className="h-32 bg-slate-700/20 rounded-xl w-full border border-dashed border-slate-600 flex items-center justify-center text-slate-500">
                                        Resume Analysis Preview
                                    </div>
                                    <div className="flex justify-between items-center pt-4">
                                        <div className="h-8 w-24 bg-green-500/20 rounded-full flex items-center justify-center text-green-400 text-sm font-bold">
                                            92/100
                                        </div>
                                        <div className="h-8 w-8 rounded-full bg-blue-500/20"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="lg:w-1/2">
                        <h2 className="text-3xl md:text-5xl font-bold mb-6">
                            Why use our <span className="gradient-text">Platform?</span>
                        </h2>
                        <p className="text-slate-400 text-lg mb-8 leading-relaxed">
                            In today's competitive job market, getting past the ATS is half the battle. Our tools are designed to give you the insights recruiters typically keep to themselves.
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {benefits.map((benefit, index) => (
                                <div key={index} className="flex items-start gap-3">
                                    <CheckCircle2 className="w-6 h-6 text-green-400 flex-shrink-0" />
                                    <span className="text-slate-300">{benefit}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                </div>
            </div>
        </section>
    );
};

export default HowItHelps;
