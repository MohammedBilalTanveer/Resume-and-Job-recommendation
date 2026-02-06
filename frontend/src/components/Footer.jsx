import React from 'react';
import { Link } from 'react-router-dom';
import { Github, Twitter, Linkedin, Heart } from 'lucide-react';

const Footer = () => {
    return (
        <footer className="bg-slate-950 border-t border-slate-800 pt-16 pb-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                    <div className="col-span-1 md:col-span-2">
                        <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
                            AI Resume Scorer
                        </h3>
                        <p className="text-slate-400 mb-6 max-w-sm">
                            Empowering job seekers with advanced AI tools to optimize resumes, find matching jobs, and land interviews faster.
                        </p>
                        <div className="flex gap-4">
                            <button type="button" className="p-2 rounded-full bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
                                <Twitter className="w-5 h-5" />
                            </button>
                            <button type="button" className="p-2 rounded-full bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
                                <Linkedin className="w-5 h-5" />
                            </button>
                            <button type="button" className="p-2 rounded-full bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
                                <Github className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Product</h4>
                        <ul className="space-y-4">
                            <li><Link to="/resume-upload" className="text-slate-400 hover:text-blue-400 transition-colors">Resume Scorer</Link></li>
                            <li><Link to="/jobs" className="text-slate-400 hover:text-blue-400 transition-colors">Job Search</Link></li>
                            <li><Link to="#" className="text-slate-400 hover:text-blue-400 transition-colors">Skill Analysis</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-bold text-white mb-6">Company</h4>
                        <ul className="space-y-4">
                            <li><Link to="#" className="text-slate-400 hover:text-blue-400 transition-colors">About Us</Link></li>
                            <li><Link to="#" className="text-slate-400 hover:text-blue-400 transition-colors">Contact</Link></li>
                            <li><Link to="#" className="text-slate-400 hover:text-blue-400 transition-colors">Privacy Policy</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-slate-900 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-slate-500 text-sm">
                        © {new Date().getFullYear()} AI Resume Scorer. All rights reserved.
                    </p>
                    <div className="flex items-center gap-1 text-slate-500 text-sm">
                        Made with <Heart className="w-4 h-4 text-red-500 fill-red-500" /> by Intellidiots
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
