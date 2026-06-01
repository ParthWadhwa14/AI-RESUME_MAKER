import React from 'react';
import { motion } from 'framer-motion';
import { ReactIcon } from 'lucide-react';

export default function SkillCard({ skill }) {
 return (
 <motion.div className="skill-card bg-gray-900 text-white p-4 rounded-lg shadow-lg hover:scale-105" whileHover={{ scale: 1.05 }}>
 <h3 className="text-xl">{skill.name}</h3>
 <ul>
 {skill.skills.map((s, index) => (
 <li key={index} className="text-lg">{s.name}</li>
 ))}
 </ul>
 <div className="proficiency flex justify-center">
 {skill.skills.map((s, index) => (
 <span key={index} className="text-lg">{s.proficiency}</span>
 ))}
 </div>
 <ReactIcon size={24} />
 </motion.div>
 );
}