import React from 'react';
import { motion } from 'framer-motion';

const experience = [
 {
 company: 'Fumind.ai',
 role: 'AI Intern',
 timeline: 'Feb - April 2026',
 highlights: [
 'Built a one-shot image segmentation pipeline using OpenCV and vision-language models to segment objects from a single reference image.',
 'Worked on AI-assisted computer vision workflows involving preprocessing, contour extraction, and prompt-guided segmentation.',
 ],
 },
];

export default function Experience() {
 return (
 <section className="experience bg-gray-800 text-white p-4 flex flex-col items-center justify-center">
 <h2 className="text-3xl">Experience</h2>
 <motion.div className="experience-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" initial="hidden" whileInView="visible" viewport={{ once: true }}>
 {experience.map((exp, index) => (
 <div key={index} className="experience-card bg-gray-900 text-white p-4 rounded-lg shadow-lg hover:scale-105">
 <h3 className="text-xl">{exp.company}</h3>
 <p className="text-lg">{exp.role}</p>
 <p className="text-lg">{exp.timeline}</p>
 <ul>
 {exp.highlights.map((highlight, index) => (
 <li key={index} className="text-lg">{highlight}</li>
 ))}
 </ul>
 </div>
 ))}
 </motion.div>
 </section>
 );
}