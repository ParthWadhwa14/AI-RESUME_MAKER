import React from 'react';
import { motion } from 'framer-motion';
import { FiGithub, FiLinkedin } from 'lucide-react';

export default function ProjectCard({ project }) {
 return (
 <motion.div
 initial={{ opacity: 0, y: 20 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.5 }}
 className="project-card flex flex-col items-center py-4 px-6 bg-gray-100 rounded-lg shadow-lg"
 >
 <h2 className="text-2xl font-bold">{project.title}</h2>
 <p className="text-xl">{project.pitch}</p>
 <ul className="list-disc ml-4">
 {project.highlights.map((highlight, index) => (
 <li key={index} className="text-lg">{highlight}</li>
 ))}
 </ul>
 <div className="tech-stack flex flex-wrap justify-center mt-4">
 {project.techStack.map((tech, index) => (
 <span key={index} className="bg-gray-200 px-2 py-1 rounded-lg mx-2 my-1">{tech}</span>
 ))}
 </div>
 </motion.div>
 );
}
