import React from 'react';
import { motion } from 'framer-motion';
import SkillCard from './SkillCard';

const skills = [
 {
 name: 'Frontend',
 skills: [
 { name: 'React', icon: 'react', proficiency: 'advanced' },
 { name: 'JavaScript', icon: 'javascript', proficiency: 'intermediate' },
 ],
 },
 {
 name: 'Backend',
 skills: [
 { name: 'Node.js', icon: 'nodejs', proficiency: 'advanced' },
 { name: 'Python', icon: 'python', proficiency: 'intermediate' },
 ],
 },
 {
 name: 'AI/ML',
 skills: [
 { name: 'TensorFlow', icon: 'tensorflow', proficiency: 'advanced' },
 { name: 'PyTorch', icon: 'pytorch', proficiency: 'intermediate' },
 ],
 },
 {
 name: 'Tools',
 skills: [
 { name: 'Git', icon: 'git', proficiency: 'advanced' },
 { name: 'GitHub', icon: 'github', proficiency: 'intermediate' },
 ],
 },
];

export default function Skills() {
 return (
 <section className="skills bg-gray-800 p-4 text-white">
 <h2 className="text-3xl font-bold mb-4">Skills</h2>
 <motion.div layout>
 {skills.map((skill, index) => (
 <SkillCard key={index} skill={skill} />
 ))}
 </motion.div>
 </section>
 );
}