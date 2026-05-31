import React from 'react';
import { motion } from 'framer-motion';

export default function SkillCard({ skill }) {
 return (
 <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className="bg-gray-700 p-4 rounded-md shadow-md mb-4">
 <div className="skill-card">
 <h3 className="text-2xl font-bold mb-2">{skill.name}</h3>
 <ul>
 {skill.skills.map((s, index) => (
 <li key={index} className="text-lg mb-2">{s.name}</li>
 ))}
 </ul>
 </div>
 </motion.div>
 );
}