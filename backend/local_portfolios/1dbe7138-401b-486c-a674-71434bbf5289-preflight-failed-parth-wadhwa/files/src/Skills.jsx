import React from 'react';
import { motion } from 'framer-motion';
import { FiGithub } from 'lucide-react';

export default function Skills() {
 const skills = [
 {
 name: 'Frontend',
 skills: [
 {
 name: 'React',
 icon: 'react',
 proficiency: 'intermediate'
 },
 {
 name: 'JavaScript',
 icon: 'javascript',
 proficiency: 'advanced'
 }
 ]
 },
 {
 name: 'Backend',
 skills: [
 {
 name: 'Node.js',
 icon: 'nodejs',
 proficiency: 'intermediate'
 },
 {
 name: 'Python',
 icon: 'python',
 proficiency: 'advanced'
 }
 ]
 },
 {
 name: 'AI/ML',
 skills: [
 {
 name: 'TensorFlow',
 icon: 'tensorflow',
 proficiency: 'intermediate'
 },
 {
 name: 'PyTorch',
 icon: 'pytorch',
 proficiency: 'advanced'
 }
 ]
 },
 {
 name: 'Tools',
 skills: [
 {
 name: 'Git',
 icon: 'git',
 proficiency: 'advanced'
 },
 {
 name: 'GitHub',
 icon: 'github',
 proficiency: 'advanced'
 }
 ]
 }
 ];

 return (
 <section className="skills">
 {skills.map((skill, index) => (
 <motion.div key={index} initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, ease: 'easeInOut' }} className="bg-glass shadow-md rounded-lg p-4">
 <h2>{skill.name}</h2>
 <ul>
 {skill.skills.map((s, index) => (
 <li key={index}>
 <span className="bg-primary text-light rounded-md py-2 px-4">
 {s.name}
 </span>
 <span className="proficiency">
 {s.proficiency}
 </span>
 </li>
 ))}
 </ul>
 </motion.div>
 ))}
 </section>
 );
}