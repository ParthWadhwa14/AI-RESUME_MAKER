import React from 'react';
import { motion } from 'framer-motion';
import { LucideReact, LucidePython, LucideNodejs } from 'lucide-react';

function Skills() {
 const skills = [
 {
 name: 'Frontend',
 skills: [
 { name: 'React', icon: <LucideReact size={24} />, proficiency: 8 },
 { name: 'JavaScript', icon: <LucideReact size={24} />, proficiency: 9 },
 ],
 },
 {
 name: 'Backend',
 skills: [
 { name: 'Node.js', icon: <LucideNodejs size={24} />, proficiency: 8 },
 { name: 'Python', icon: <LucidePython size={24} />, proficiency: 9 },
 ],
 },
 ];

 return (
 <motion.section initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ duration: 0.3 }} className="section">
 <h2>Skills</h2>
 <div className="skills-grid">
 {skills.map((skill, index) => (
 <div key={index} className="skill-category">
 <h3>{skill.name}</h3>
 <ul>
 {skill.skills.map((s, index) => (
 <li key={index}>{s.name} {s.icon}</li>
 ))}
 </ul>
 </div>
 ))}
 </div>
 </motion.section>
 );
}

export default Skills;