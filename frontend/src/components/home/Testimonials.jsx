import React from 'react';
import { Star } from 'lucide-react';

const testimonials = [
    {
        name: "Sarah Jenkins",
        role: "Marketing Manager",
        content: "I was applying to 50+ jobs a week with no response. After using this ATS scorer, I realized my resume was unreadable by bots. Fixed it, and got 3 interviews in a week!",
        rating: 5
    },
    {
        name: "Michael Chen",
        role: "Software Engineer",
        content: "The skill gap analysis is a game saver. It told me exactly which keywords I was missing for Senior Dev roles. Highly recommended.",
        rating: 5
    },
    {
        name: "Elena Rodriguez",
        role: "Data Analyst",
        content: "Simple, fast, and effective. The realistic UI is a nice bonus too - makes the whole stressful process feel a bit more high-tech and manageable.",
        rating: 4
    }
];

const Testimonials = () => {
    return (
        <section className="py-24 bg-slate-800/50 relative overflow-hidden">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-4">
                        Success <span className="gradient-text">Stories</span>
                    </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {testimonials.map((testimonial, index) => (
                        <div key={index} className="glass-card flex flex-col h-full">
                            <div className="flex mb-4">
                                {[...Array(5)].map((_, i) => (
                                    <Star
                                        key={i}
                                        className={`w-5 h-5 ${i < testimonial.rating ? 'text-yellow-400 fill-yellow-400' : 'text-slate-600'}`}
                                    />
                                ))}
                            </div>
                            <p className="text-slate-300 mb-6 flex-grow italic">"{testimonial.content}"</p>
                            <div className="flex items-center gap-4 mt-auto">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center font-bold text-white">
                                    {testimonial.name[0]}
                                </div>
                                <div>
                                    <div className="font-bold text-white">{testimonial.name}</div>
                                    <div className="text-sm text-slate-500">{testimonial.role}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Testimonials;
