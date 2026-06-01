import React from 'react';
import { motion } from 'framer-motion';
import { LucideReact, LucidePython, LucideNodejs } from 'lucide-react';

function ProjectCard({ project }) {
 return (
 <motion.div initial={{ opacity: 0, y: 100 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="project-card">
 <h3>{project.title}</h3>
 <p>{project.pitch}</p>
 <ul>
 {project.highlights.map((highlight, index) => (
 <li key={index}>{highlight}</li>
 ))}
 </ul>
 <div className="tech-stack">
 {project.techStack.map((tech, index) => (
 <span key={index}>{tech}</span>
 ))}
 </div>
 </motion.div>
 );
}

export default ProjectCard;