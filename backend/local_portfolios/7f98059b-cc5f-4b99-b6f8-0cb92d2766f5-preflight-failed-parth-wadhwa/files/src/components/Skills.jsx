import React from 'react';
import { FiReact } from 'lucide-react';

export default function Skills() {
 return (
 <section className="skills">
 <h2>Skills</h2>
 <ul>
 <li>
 <h3>Frontend</h3>
 <ul>
 <li>
 <FiReact size={20} />
 React
 </li>
 <li>JavaScript</li>
 </ul>
 </li>
 <li>
 <h3>Backend</h3>
 <ul>
 <li>Node.js</li>
 <li>Python</li>
 </ul>
 </li>
 <li>
 <h3>AI/ML</h3>
 <ul>
 <li>TensorFlow</li>
 <li>PyTorch</li>
 </ul>
 </li>
 <li>
 <h3>Tools</h3>
 <ul>
 <li>Git</li>
 <li>GitHub</li>
 </ul>
 </li>
 </ul>
 </section>
 );
}
