import React from 'react';
import { Upload, Cpu, Briefcase, Send } from 'lucide-react';

const steps = [
    {
        icon: <Upload className="w-6 h-6" />,
        title: "Upload Resume",
        description: "Upload your existing resume in PDF format to our secure platform."
    },
    {
        icon: <Cpu className="w-6 h-6" />,
        title: "AI Analysis",
        description: "Our advanced algorithms analyze your skills, experience, and formatting."
    },
    {
        icon: <Briefcase className="w-6 h-6" />,
        title: "Get Matches",
        description: "Receive personalized job recommendations based on your unique profile."
    },
    {
        icon: <Send className="w-6 h-6" />,
        title: "Apply with Confidence",
        description: "Apply to jobs knowing your resume is optimized for their specific requirements."
    }
];

const HowItWorks = () => {
    return (
        <section className="py-24 bg-slate-800/50 relative overflow-hidden" id="how-it-works">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-4">
                        How it <span className="gradient-text">Works</span>
                    </h2>
                    <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                        Your journey to a better career is just four simple steps away.
                    </p>
                </div>

                <div className="relative">
                    {/* Connector Line (Desktop) */}
                    <div className="hidden lg:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-blue-500/0 via-blue-500/50 to-blue-500/0 -translate-y-1/2 z-0"></div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {steps.map((step, index) => (
                            <div key={index} className="relative z-10 group">
                                <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 hover:border-blue-500 transition-colors text-center h-full flex flex-col items-center">
                                    <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-110 group-hover:bg-blue-600 group-hover:text-white transition-all duration-300 shadow-[0_0_15px_rgba(59,130,246,0.3)]">
                                        {step.icon}
                                    </div>
                                    <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-slate-500">
                                        {index + 1}
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                                    <p className="text-slate-400 text-sm">{step.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
