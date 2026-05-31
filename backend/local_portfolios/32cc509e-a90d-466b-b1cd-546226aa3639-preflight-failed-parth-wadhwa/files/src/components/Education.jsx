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
 <section className="education bg-gray-800 p-4 text-white">
 <h2 className="text-3xl font-bold mb-4">Education</h2>
 <motion.div layout>
 {education.map((edu, index) => (
 <div key={index} className="bg-gray-700 p-4 rounded-md shadow-md mb-4">
 <h3 className="text-2xl font-bold mb-2">{edu.institution}</h3>
 <p className="text-xl mb-2">{edu.degree}</p>
 <p className="text-lg mb-2">{edu.timeline}</p>
 </div>
 ))}
 </motion.div>
 </section>
 );
}