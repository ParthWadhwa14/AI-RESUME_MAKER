import React from 'react';
import { motion } from 'framer-motion';
import { FiReact, FiJavascript, FiNodejs, FiPython, FiLanggraph, FiOpenai, FiGit, FiGithub } from 'lucide-react';

export default function SkillCard({ skill }) {
 return (
 <motion.div
 initial={{ opacity: 0, y: 20 }}
 animate={{ opacity: 1, y: 0 }}
 transition={{ duration: 0.5 }}
 className="skill-card flex flex-col items-center py-4 px-6 bg-gray-100 rounded-lg shadow-lg"
 >
 <h2 className="text-2xl font-bold">{skill.name}</h2>
 <ul className="list-disc ml-4">
 {skill.skills.map((s, index) => (
 <li key={index} className="text-lg flex items-center">
 {s.icon === 'react' && <FiReact size={24} className="mr-2" />}
 {s.icon === 'javascript' && <FiJavascript size={24} className="mr-2" />}
 {s.icon === 'nodejs' && <FiNodejs size={24} className="mr-2" />}
 {s.icon === 'python' && <FiPython size={24} className="mr-2" />}
 {s.icon === 'langgraph' && <FiLanggraph size={24} className="mr-2" />}
 {s.icon === 'openai' && <FiOpenai size={24} className="mr-2" />}
 {s.icon === 'git' && <FiGit size={24} className="mr-2" />}
 {s.icon === 'github' && <FiGithub size={24} className="mr-2" />}
 <span>{s.name}</span>
 <span className="text-gray-500"> - {s.proficiency}</span>
 </li>
 ))}
 </ul>
 </motion.div>
 );
}
