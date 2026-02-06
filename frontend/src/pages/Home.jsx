import React from 'react';
import Hero from '../components/home/Hero';
import Features from '../components/home/Features';
import HowItWorks from '../components/home/HowItWorks';
import HowItHelps from '../components/home/HowItHelps';
import Testimonials from '../components/home/Testimonials';
import CTA from '../components/home/CTA';
import Footer from '../components/Footer';

export const Home = () => {
  return (
    <div className="bg-slate-900 min-h-screen text-slate-200">
      <Hero />
      <Features />
      <HowItWorks />
      <HowItHelps />
      <Testimonials />
      <CTA />
      <Footer />
    </div>
  );
};
