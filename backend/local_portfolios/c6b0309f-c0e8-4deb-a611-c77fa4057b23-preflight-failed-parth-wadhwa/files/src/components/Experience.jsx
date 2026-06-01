import React from 'react';
import { motion } from 'framer-motion';

const Experience = () => {
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

 return (
 <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="bg-white p-4 shadow-md">
 <h2 className="text-3xl font-bold">Experience</h2>
 <ul>
 {experience.map((item, index) => (
 <li key={index} className="mb-4">
 <h3 className="text-2xl font-bold">{item.company}</h3>
 <p className="text-xl">{item.role} ({item.timeline})</p>
 <ul>
 {item.highlights.map((highlight, index) => (
 <li key={index} className="text-lg">{highlight}</li>
 ))}
 </ul>
 </li>
 ))}
 </ul>
 </motion.section>
 );
};

export default Experience;
