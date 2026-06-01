import React from 'react';
import { Github, Linkedin } from 'lucide-react';

const Hero = () => {
 return (
 <section className="hero">
 <h1>Parth Wadhwa</h1>
 <p>AI Full-Stack Developer</p>
 <div className="social-links">
 <a href="https://github.com/ParthWadhwa14" target="_blank" rel="noopener noreferrer">
 <AiOutlineGithub size={24} />
 </a>
 <a href="https://www.linkedin.com/in/parth-wadhwa-855650323/" target="_blank" rel="noopener noreferrer">
 <AiOutlineLinkedin size={24} />
 </a>
 </div>
 </section>
 );
};

export default Hero;
