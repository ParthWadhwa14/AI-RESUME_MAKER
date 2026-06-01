import React from 'react';
import { motion } from 'framer-motion';

const education = [
 {
 institution: 'Indian Institute of Technology (IIT) Delhi',
 degree: 'B.Tech in Chemical Engineering',
 timeline: '2024 - Present',
 },
];

export default function Education() {
 return (
 <section className="education bg-gray-800 text-white p-4 flex flex-col items-center justify-center">
 <h2 className="text-3xl">Education</h2>
 <motion.div className="education-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" initial="hidden" whileInView="visible" viewport={{ once: true }}>
 {education.map((edu, index) => (
 <div key={index} className="education-card bg-gray-900 text-white p-4 rounded-lg shadow-lg hover:scale-105">
 <h3 className="text-xl">{edu.institution}</h3>
 <p className="text-lg">{edu.degree}</p>
 <p className="text-lg">{edu.timeline}</p>
 </div>
 ))}
 </motion.div>
 </section>
 );
}