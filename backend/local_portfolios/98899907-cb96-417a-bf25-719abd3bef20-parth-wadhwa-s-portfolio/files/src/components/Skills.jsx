import React from 'react';
import { motion } from 'framer-motion';
import { AiOutlineReact, AiOutlineNodejs, AiOutlineTensorflow, AiOutlinePytorch, AiOutlineGit, AiOutlineGithub } from 'lucide-react';

const Skills = () => {
 const skills = [
 {
 name: 'Frontend',
 skills: [
 {
 name: 'React',
 icon: <AiOutlineReact size={24} />, 
 proficiency: 'Intermediate'
 },
 ],
 },
 {
 name: 'Backend',
 skills: [
 {
 name: 'Node.js',
 icon: <AiOutlineNodejs size={24} />, 
 proficiency: 'Intermediate'
 },
 ],
 },
 {
 name: 'AI/ML',
 skills: [
 {
 name: 'TensorFlow',
 icon: <AiOutlineTensorflow size={24} />, 
 proficiency: 'Beginner'
 },
 {
 name: 'PyTorch',
 icon: <AiOutlinePytorch size={24} />, 
 proficiency: 'Beginner'
 },
 ],
 },
 {
 name: 'Tools',
 skills: [
 {
 name: 'Git',
 icon: <AiOutlineGit size={24} />, 
 proficiency: 'Advanced'
 },
 {
 name: 'GitHub',
 icon: <AiOutlineGithub size={24} />, 
 proficiency: 'Advanced'
 },
 ],
 },
 ];

 return (
 <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="bg-white p-4 shadow-md">
 <h2 className="text-3xl font-bold">Skills</h2>
 <ul>
 {skills.map((category, index) => (
 <li key={index} className="mb-4">
 <h3 className="text-2xl font-bold">{category.name}</h3>
 <ul>
 {category.skills.map((skill, index) => (
 <li key={index} className="flex items-center justify-center">
 {skill.icon}
 <span className="text-lg">{skill.name}</span>
 <span className="text-lg">{skill.proficiency}</span>
 </li>
 ))}
 </ul>
 </li>
 ))}
 </ul>
 </motion.section>
 );
};

export default Skills;
