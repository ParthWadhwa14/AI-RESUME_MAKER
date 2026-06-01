import React from 'react';
import { motion } from 'framer-motion';

function Education() {
 const education = [
 {
 institution: 'Indian Institute of Technology (IIT) Delhi',
 degree: 'B.Tech in Chemical Engineering',
 timeline: '2024 - Present',
 },
 ];

 return (
 <motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ duration: 0.3 }} className="section">
 <h2>Education</h2>
 <ul>
 {education.map((edu, index) => (
 <li key={index}>{edu.institution} - {edu.degree} ({edu.timeline})</li>
 ))}
 </ul>
 </motion.section>
 );
}

export default Education;