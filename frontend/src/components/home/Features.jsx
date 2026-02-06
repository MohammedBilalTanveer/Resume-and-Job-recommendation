import React from 'react';
import {
    FileText,
    Target,
    TrendingUp,
    Search,
    Brain,
    Shield
} from 'lucide-react';

const params = [
    {
        icon: <FileText className="w-8 h-8 text-blue-400" />,
        title: "Smart Resume Analysis",
        description: "Our AI breaks down your resume to identify key strengths, weaknesses, and optimization opportunities for specific job roles."
    },
    {
        icon: <Target className="w-8 h-8 text-purple-400" />,
        title: "ATS Compatibility",
        description: "Get a detailed ATS score and actionable insights to ensure your resume passes automated screening systems."
    },
    {
        icon: <Search className="w-8 h-8 text-pink-400" />,
        title: "Intelligent Job Search",
        description: "Find jobs that match your skills across multiple platforms like Remotive, Adzuna, and Jooble."
    },
    {
        icon: <Brain className="w-8 h-8 text-indigo-400" />,
        title: "Skill Gap Analysis",
        description: "Identify missing skills required for your target roles and get recommendations on how to acquire them."
    },
    {
        icon: <TrendingUp className="w-8 h-8 text-green-400" />,
        title: "Market Trends",
        description: "Stay ahead with real-time insights into the most in-demand skills and trending job roles in your industry."
    },
    {
        icon: <Shield className="w-8 h-8 text-yellow-400" />,
        title: "Secure & Private",
        description: "Your data is encrypted and secure. We focus on your privacy while helping you advance your career."
    }
];

const Features = () => {
    return (
        <section className="relative py-24 bg-slate-900 overflow-hidden" id="features">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">

                <div className="absolute -top-24 -right-24 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
                <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-widest mb-3">Powerful Features</h2>
                    <h3 className="text-3xl md:text-5xl font-bold mb-6">
                        Everything you need to <span className="gradient-text">land your dream job</span>
                    </h3>
                    <p className="text-slate-400 text-lg">
                        Our platform combines advanced machine learning with industry insights to give you the competitive edge in your job search.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {params.map((feature, index) => (
                        <div
                            key={index}
                            className="glass-card hover:-translate-y-2 group"
                        >
                            <div className="mb-6 p-3 rounded-xl bg-white/5 w-fit group-hover:bg-white/10 transition-colors">
                                {feature.icon}
                            </div>
                            <h4 className="text-xl font-bold text-white mb-3 group-hover:text-blue-400 transition-colors">
                                {feature.title}
                            </h4>
                            <p className="text-slate-400 leading-relaxed">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Features;
