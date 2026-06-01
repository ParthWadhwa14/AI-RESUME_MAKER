import React from 'react';
import { motion } from 'framer-motion';
import SkillCard from './SkillCard';

const skills = [
 {
 name: 'Frontend',
 skills: [
 { name: 'React', icon: 'react', proficiency: 'intermediate' },
 { name: 'JavaScript', icon: 'javascript', proficiency: 'advanced' },
 ],
 },
 {
 name: 'Backend',
 skills: [
 { name: 'Node.js', icon: 'nodejs', proficiency: 'intermediate' },
 { name: 'Python', icon: 'python', proficiency: 'advanced' },
 ],
 },
];

export default function Skills() {
 return (
 <section className="skills bg-gray-800 text-white p-4 flex flex-col items-center justify-center">
 <h2 className="text-3xl">Skills</h2>
 <motion.div className="skill-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" initial="hidden" whileInView="visible" viewport={{ once: true }}>
 {skills.map((skill, index) => (
 <SkillCard key={index} skill={skill} />
 ))}
 </motion.div>
 </section>
 );
}