import React, { useState, useEffect } from 'react';
import Slider from '../components/Slider';
import Testimonials from '../components/Testimonials';
import Partners from '../components/Partners';

const slidesData = [
  {
    title: "Life Happens. Food Shouldn’t Be Optional.",
    bulletPoints: [
      "Unexpected expenses force people to cut food budgets.",
      "Millions skip meals or eat unhealthy because money ran out.",
      "No system currently guarantees consistent access to nutritious meals.",
      "Food insecurity affects health, focus, productivity, and dignity."
    ],
    cta: "Learn More"
  },
  {
    title: "A Meal Subscription That Has Your Back.",
    bulletPoints: [
      "Kularashio lets users subscribe to affordable, prepaid meal plans.",
      "Meals stay consistent even when finances fluctuate.",
      "Helps users stick to a food budget and avoid last-minute food stress.",
      "Partners with restaurants to provide reliable, quality meals."
    ],
    cta: "Subscribe Now"
  },
  {
    title: "A Smart Platform That Feeds and Empowers.",
    bulletPoints: [
      "AI-powered assistant curates personalized meal plans.",
      "Users choose dietary needs, frequency, and pickup/delivery options.",
      "Tracks food budgets and prevents overspending.",
      "Connects users to local restaurants and ensures real-time access to meals.",
      "Available on mobile & web. Built for simplicity, speed, and scale."
    ],
    cta: "Try It Today"
  }
];

function LandingPage() {
  return (
    <div className="bg-brand-white text-gray-900">
      {/* Navigation, Header, etc. can be another component */}
      <Slider slides={slidesData} />
      <section className="container mx-auto py-12">
        {/* Images / Product Visuals */}
        <div className="flex flex-wrap justify-center gap-8">
          <img className="rounded shadow-lg" src="https://via.placeholder.com/300x200.png?text=Product+Image+1" alt="Product 1" />
          <img className="rounded shadow-lg" src="https://via.placeholder.com/300x200.png?text=Product+Image+2" alt="Product 2" />
          <img className="rounded shadow-lg" src="https://via.placeholder.com/300x200.png?text=Product+Image+3" alt="Product 3" />
        </div>
      </section>
      <Testimonials />
      <Partners />
      <section id="cta" className="bg-brand-red text-brand-yellow py-12 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready To Take Control?</h2>
        <p className="mb-8">Join Kularashio today and experience a smarter, stress-free way to budget your meals!</p>
        <button className="bg-brand-yellow text-brand-red px-8 py-3 rounded font-bold hover:opacity-90" onClick={() => window.location.href='/signup'}>Sign Up Now</button>
      </section>
    </div>
  );
}

export default LandingPage;
