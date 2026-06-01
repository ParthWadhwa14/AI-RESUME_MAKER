import React from 'react';
import { motion } from 'framer-motion';
import SkillCard from './SkillCard';

const skills = [
 {
 name: 'Frontend',
 skills: [
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
 ],
 },
 {
 name: 'Backend',
 skills: [
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
 ],
 },
 {
 name: 'AI/ML',
 skills: [
 {
 name: 'LangGraph',
 icon: 'langgraph',
 proficiency: 'advanced',
 },
 {
 name: 'OpenAI API / SDK',
 icon: 'openai',
 proficiency: 'intermediate',
 },
 ],
 },
 {
 name: 'Tools',
 skills: [
 {
 name: 'Git',
 icon: 'git',
 proficiency: 'advanced',
 },
 {
 name: 'GitHub',
 icon: 'github',
 proficiency: 'intermediate',
 },
 ],
 },
];

export default function Skills() {
 return (
 <section className="skills flex flex-col items-center py-4">
 <h1 className="text-3xl font-bold">Skills</h1>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.5 }}
 >
 {skills.map((skill, index) => (
 <SkillCard key={index} skill={skill} />
 ))}
 </motion.div>
 </section>
 );
}
