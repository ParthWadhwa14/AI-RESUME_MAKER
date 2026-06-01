import React from 'react';
import { motion } from 'framer-motion';
import SkillCard from './SkillCard';

const skills = [
 {
 name: 'React',
 icon: 'react',
 proficiency: 'advanced',
 },
 {
 name: 'JavaScript',
 icon: 'javascript',
 proficiency: 'intermediate',
 },
 {
 name: 'Node.js',
 icon: 'nodejs',
 proficiency: 'advanced',
 },
 {
 name: 'Python',
 icon: 'python',
 proficiency: 'intermediate',
 },
 {
 name: 'TensorFlow',
 icon: 'tensorflow',
 proficiency: 'intermediate',
 },
 {
 name: 'PyTorch',
 icon: 'pytorch',
 proficiency: 'intermediate',
 },
 {
 name: 'Git',
 icon: 'git',
 proficiency: 'advanced',
 },
 {
 name: 'GitHub',
 icon: 'github',
 proficiency: 'advanced',
 },
];

const Skills = () => {
 return (
 <section className="skills">
 <h2>Skills</h2>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 {skills.map((skill, index) => (
 <SkillCard key={index} skill={skill} />
 ))}
 </motion.div>
 </section>
 );
};

export default Skills;
