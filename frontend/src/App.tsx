/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion, useScroll, useTransform, AnimatePresence } from "motion/react";
import { MoveRight, Landmark, ShieldCheck, Scale, FileText, Lock, Mail, CheckCircle2, Building2, Building, Briefcase, Users, FileEdit, Play, Globe } from "lucide-react";
import { useEffect, useState, useRef } from "react";

const DustMotes = () => {
  const [motes, setMotes] = useState<{ id: number; left: string; size: string; duration: string; delay: string }[]>([]);

  useEffect(() => {
    const newMotes = Array.from({ length: 50 }).map((_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      size: `${Math.random() * 2 + 1}px`,
      duration: `${Math.random() * 15 + 15}s`,
      delay: `${Math.random() * 10}s`,
    }));
    setMotes(newMotes);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-10 overflow-hidden">
      {motes.map((mote) => (
        <div
          key={mote.id}
          className="dust-mote opacity-0"
          style={{
            left: mote.left,
            bottom: "-20px",
            width: mote.size,
            height: mote.size,
            boxShadow: `0 0 12px rgba(184, 155, 114, 0.5)`,
            animation: `float-mote ${mote.duration} linear infinite`,
            animationDelay: mote.delay,
          }}
        />
      ))}
    </div>
  );
};

const TypewriterText = ({ text, delay = 0 }: { text: string; delay?: number }) => {
  const characters = Array.from(text);
  
  const container = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.02, delayChildren: delay }
    }
  };

  const child = {
    visible: {
      opacity: 1,
      transition: {
        duration: 0.1
      }
    },
    hidden: {
      opacity: 0
    }
  };

  return (
    <motion.h2
      variants={container}
      initial="hidden"
      animate="visible"
      className="font-serif text-3xl md:text-4xl text-govern-silk leading-relaxed italic opacity-90"
    >
      {characters.map((char, index) => (
        <motion.span variants={child} key={index} className="inline-block">
          {char === " " ? "\u00A0" : char}
        </motion.span>
      ))}
    </motion.h2>
  );
};

const OnboardingPage = ({ onComplete }: { onComplete: () => void }) => {
  const [step, setStep] = useState(1);
  const [answers, setAnswers] = useState({ workLocation: "", workShape: "" });

  const finalMessage = "Your simulation is ready. The scenarios ahead are drawn from real governance situations. There are no right answers — only decisions and their consequences.";

  const locations = [
    { id: "hq", label: "Central Headquarters", icon: Landmark, desc: "Cabinet Secretariat, PMO, or Central Ministries" },
    { id: "state", label: "State Secretariat", icon: Building2, desc: "Departmental Headquarters in State Capitals" },
    { id: "field", label: "District or Field", icon: Briefcase, desc: "Collectorates, Police HQs, or Block Administration" },
    { id: "psu", label: "PSU or Regulatory Authority", icon: Building, desc: "Statutory Bodies, PSUs, or Public Commissions" }
  ];

  const shapes = [
    { id: "policy", label: "Drafting, reviewing, or approving policies and files", icon: FileEdit },
    { id: "pilots", label: "Running programmes or pilots", icon: Play },
    { id: "implementation", label: "Field implementation and citizen interface", icon: Users },
    { id: "other", label: "Other Administrative Functions", icon: Globe }
  ];

  const handleSelect = (id: string) => {
    if (step === 1) {
      setAnswers(prev => ({ ...prev, workLocation: id }));
      setTimeout(() => setStep(2), 600);
    } else {
      setAnswers(prev => ({ ...prev, workShape: id }));
      setTimeout(() => setStep(3), 600);
    }
  };

  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center p-6 bg-govern-charcoal">
      <div className="absolute inset-0 institutional-grid-fine opacity-30 z-0" />
      <div className="absolute top-20 left-1/2 -translate-x-1/2 flex gap-4 z-10">
        <div className={`w-2 h-2 rounded-full transition-all duration-500 ${step >= 1 ? "bg-govern-gold w-6" : "bg-govern-gold/20"}`} />
        <div className={`w-2 h-2 rounded-full transition-all duration-500 ${step >= 2 ? "bg-govern-gold w-6" : "bg-govern-gold/20"}`} />
      </div>

      <AnimatePresence mode="wait">
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, scale: 0.98, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 1.02, y: -10 }}
            className="w-full max-w-4xl space-y-12 text-center"
          >
            <div className="space-y-4">
              <h2 className="font-display text-4xl md:text-5xl text-govern-silk">Where do you primarily work?</h2>
              <p className="text-govern-gold/40 text-[10px] tracking-[0.4em] uppercase">Context Identification</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {locations.map((loc) => (
                <button
                  key={loc.id}
                  onClick={() => handleSelect(loc.id)}
                  className={`group relative p-8 glass-card text-left transition-all duration-500 hover:border-govern-gold/40 ${answers.workLocation === loc.id ? "bg-govern-gold/10 border-govern-gold/60 scale-[0.98]" : ""}`}
                >
                  <div className="flex gap-6 items-center">
                    <div className={`p-4 border border-govern-gold/10 rounded-sm transition-colors duration-500 ${answers.workLocation === loc.id ? "bg-govern-gold text-govern-charcoal" : "text-govern-gold/40 group-hover:text-govern-gold/80"}`}>
                      <loc.icon className="w-6 h-6" strokeWidth={1} />
                    </div>
                    <div className="space-y-1">
                      <h3 className="font-serif text-xl text-govern-silk italic">{loc.label}</h3>
                      <p className="text-[10px] text-govern-silk/30 uppercase tracking-[0.1em]">{loc.desc}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, scale: 0.98, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 1.02, y: -10 }}
            className="w-full max-w-4xl space-y-12 text-center"
          >
            <div className="space-y-4">
              <h2 className="font-display text-4xl md:text-5xl text-govern-silk">What is the main shape of your work?</h2>
              <p className="text-govern-gold/40 text-[10px] tracking-[0.4em] uppercase">Functional Classification</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {shapes.map((shape) => (
                <button
                  key={shape.id}
                  onClick={() => handleSelect(shape.id)}
                  className={`group relative p-8 glass-card text-left transition-all duration-500 hover:border-govern-gold/40 ${answers.workShape === shape.id ? "bg-govern-gold/10 border-govern-gold/60 scale-[0.98]" : ""}`}
                >
                  <div className="flex gap-6 items-center">
                    <div className={`p-4 border border-govern-gold/10 rounded-sm transition-colors duration-500 ${answers.workShape === shape.id ? "bg-govern-gold text-govern-charcoal" : "text-govern-gold/40 group-hover:text-govern-gold/80"}`}>
                      <shape.icon className="w-6 h-6" strokeWidth={1} />
                    </div>
                    <h3 className="font-serif text-xl text-govern-silk italic leading-tight">{shape.label}</h3>
                  </div>
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full max-w-2xl text-center space-y-12"
          >
            <div className="relative inline-block py-12 px-16 border-y border-govern-gold/10">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-govern-charcoal px-6">
                 <ShieldCheck className="w-8 h-8 text-govern-gold/40" strokeWidth={1} />
              </div>
              <TypewriterText text={finalMessage} delay={0.5} />
            </div>

            <motion.button
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + (finalMessage.length * 0.02), duration: 1 }}
              onClick={onComplete}
              className="group relative px-20 py-5 bg-govern-gold text-govern-charcoal font-bold text-xs tracking-[0.5em] uppercase hover:-translate-y-1 transition-all duration-500"
            >
              Begin Simulation
              <MoveRight className="inline-block ml-4 w-4 h-4 group-hover:translate-x-4 transition-transform" />
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const LoginPage = ({ onBack, onVerify }: { onBack: () => void, onVerify: () => void }) => {
  const [email, setEmail] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) setIsSubmitted(true);
  };

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-6">
      {/* Background for Login Context */}
      <div className="absolute inset-0 bg-govern-charcoal z-0" />
      <div className="absolute inset-0 institutional-grid-fine z-0" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(184,155,114,0.05)_0%,transparent_70%)] z-0" />

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="glass-card relative w-full max-w-md p-10 md:p-12 z-10 overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {!isSubmitted ? (
            <motion.div
              key="login-form"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-10"
            >
              <div className="flex flex-col items-center text-center space-y-4">
                <Landmark className="w-10 h-10 text-govern-gold" strokeWidth={1} />
                <div className="space-y-2">
                  <h2 className="font-display text-3xl text-govern-silk">GovernAI Studio</h2>
                  <p className="text-govern-gold/50 text-[10px] tracking-[0.3em] uppercase">Sign in to your simulation</p>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="space-y-3">
                  <label htmlFor="email" className="block text-[9px] uppercase tracking-[0.3em] text-govern-gold/50 ml-1 font-bold">
                    Institutional Email Identifier
                  </label>
                  <input
                    type="email"
                    id="email"
                    placeholder="your.name@gov.in"
                    className="login-input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="w-full group relative py-5 bg-govern-gold text-govern-charcoal font-bold text-[10px] tracking-[0.4em] uppercase overflow-hidden transition-all duration-500 hover:-translate-y-[1px] hover:shadow-[0_15px_40px_rgba(184,155,114,0.25)] rounded-sm"
                >
                  <span className="relative z-10">
                    Propagate Secure Link
                  </span>
                  <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              </form>

              <div className="flex flex-col items-center justify-center gap-6 pt-6 border-t border-govern-gold/10">
                <div className="flex items-center gap-3 text-govern-silk/20">
                  <Lock className="w-3.5 h-3.5" />
                  <span className="text-[8px] uppercase tracking-[0.2em] font-medium">Digital Public Infrastructure • Encrypted Connection</span>
                </div>
                <button 
                  onClick={onBack}
                  className="text-[9px] uppercase tracking-[0.4em] text-govern-silk/20 hover:text-govern-silk transition-colors"
                >
                  Return to Entry Protocol
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="success-message"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center space-y-10 py-12"
            >
              <div className="relative flex justify-center">
                <div className="absolute inset-0 bg-govern-gold/10 blur-3xl rounded-full" />
                <svg className="w-20 h-20 text-govern-gold relative z-10" viewBox="0 0 100 100">
                  <circle 
                    className="opacity-10" 
                    cx="50" 
                    cy="50" 
                    r="45" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                  />
                  <motion.path 
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 1.5, ease: "easeInOut" }}
                    d="M30 50 L45 65 L70 35" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="4" 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                  />
                </svg>
              </div>

              <div className="space-y-6">
                <h3 className="font-display text-3xl text-govern-silk leading-tight">Verification In Transit</h3>
                <p className="text-govern-silk/40 text-[10px] leading-relaxed uppercase tracking-[0.2em] max-w-[280px] mx-auto">
                  A secure access token has been dispatched to your verified government domain.
                </p>
              </div>

              <div className="flex flex-col items-center gap-4">
                <button 
                  onClick={onVerify}
                  className="group relative px-12 py-4 bg-govern-gold text-govern-charcoal font-bold text-[10px] tracking-[0.3em] uppercase rounded-sm hover:-translate-y-1 transition-all"
                >
                  Proceed to Onboarding
                </button>
                <button 
                  onClick={onBack}
                  className="text-[9px] uppercase tracking-[0.4em] text-govern-gold/40 hover:text-govern-gold transition-colors pt-2"
                >
                  Return to Entry Protocol
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default function App() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentScreen, setCurrentScreen] = useState<"landing" | "login" | "onboarding">("landing");
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 1.1]);

  return (
    <div ref={containerRef} className="relative min-h-[150vh] bg-govern-charcoal text-govern-silk selection:bg-govern-gold selection:text-govern-charcoal">
      <div className="grain-overlay" />
      <DustMotes />

      <AnimatePresence>
        {currentScreen === "login" && (
          <LoginPage 
            onBack={() => setCurrentScreen("landing")} 
            onVerify={() => setCurrentScreen("onboarding")}
          />
        )}
        {currentScreen === "onboarding" && (
          <OnboardingPage onComplete={() => setCurrentScreen("landing")} />
        )}
      </AnimatePresence>
      
      {/* Top Protocol Rail */}
      <nav className="fixed top-0 inset-x-0 h-10 border-b border-govern-gold/10 bg-govern-charcoal/90 backdrop-blur-xl z-[100] overflow-hidden flex items-center">
        <motion.div 
          initial={{ x: "0%" }}
          animate={{ x: "-50%" }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          className="flex whitespace-nowrap items-center"
        >
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex items-center gap-12 px-6 text-[8px] font-sans tracking-[0.5em] uppercase text-govern-silk/40">
              <span className="flex items-center gap-3">
                <div className="w-1 h-1 rounded-full bg-govern-gold/60 animate-pulse" />
                Protocol: Active
              </span>
              <span className="opacity-40">&bull;</span>
              <span>Clearance: JS/AS Level Required</span>
              <span className="opacity-40">&bull;</span>
              <span>Digital India Implementation Unit</span>
              <span className="opacity-40">&bull;</span>
              <span>Status: Simulation Operational</span>
              <span className="opacity-40">&bull;</span>
              <span>Node: New Delhi / HQ-01</span>
            </div>
          ))}
        </motion.div>
      </nav>

      {/* Cinematic Background Layer */}
      <div className="fixed inset-0 z-0 overflow-hidden">
        <motion.div 
          style={{ scale }}
          className="relative w-full h-full"
        >
          {/* Main Background Image - Atmosphere of an institutional building */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat grayscale opacity-[0.1]"
            style={{ 
              backgroundImage: `url('https://images.unsplash.com/photo-1594913785162-e6786b42dea3?q=80&w=2670&auto=format&fit=crop')`, 
            }} 
          />

          {/* Depth Overlays */}
          <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black opacity-95" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,transparent_0%,rgba(5,5,5,0.98)_95%)]" />
          <div className="absolute inset-0 institutional-grid opacity-30" />
        </motion.div>
      </div>

      {/* Main Hero Viewport */}
      <section className="relative h-screen flex flex-col items-center justify-center p-6 text-center z-20">
        <motion.div
           initial={{ opacity: 0, y: 15 }}
           animate={{ opacity: 1, y: 0 }}
           transition={{ duration: 3, ease: [0.16, 1, 0.3, 1] }}
           className="max-w-5xl"
        >
          <header className="mb-16 relative">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 0.05, scale: 1 }}
              transition={{ duration: 8 }}
              className="absolute -top-8 left-1/2 -translate-x-1/2 pointer-events-none z-0"
            >
              <Landmark className="w-[30rem] h-[30rem] text-govern-gold" />
            </motion.div>
            
            <motion.h1 
              className="font-display text-7xl md:text-9xl lg:text-[10rem] tracking-tight text-govern-silk text-letterpress relative z-10 font-medium leading-[0.85] mb-4"
              style={{ fontDisplay: 'swap' }}
            >
              GovernAI Studio
            </motion.h1>

            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: '120px' }}
              transition={{ delay: 1.5, duration: 3 }}
              className="h-[1px] bg-govern-gold/40 mx-auto my-10"
            />

            <motion.p 
              initial={{ opacity: 0, letterSpacing: '0.5em' }}
              animate={{ opacity: 0.8, letterSpacing: '0.5em' }}
              transition={{ delay: 2, duration: 3 }}
              className="font-sans text-[10px] md:text-xs uppercase font-semibold text-govern-gold tracking-[0.5em] ml-[0.5em] italic opacity-60"
            >
              National Scenario Simulation Lab
            </motion.p>
          </header>

          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 3, duration: 2.5 }}
              className="mt-12 flex flex-col items-center gap-12"
            >
              <button 
                onClick={() => setCurrentScreen("login")}
                id="initialize-simulation-btn"
                className="group relative px-20 py-5 bg-[#141815] text-govern-silk font-bold text-[10px] tracking-[0.5em] uppercase hover:text-govern-gold transition-all duration-1000 border border-govern-gold/20 hover:border-govern-gold/50 shadow-[0_30px_60px_rgba(0,0,0,0.8)] overflow-hidden rounded-sm"
              >
                <div className="absolute inset-x-0 top-0 h-px bg-govern-gold/30 opacity-20" />
                <div className="absolute inset-0 bg-govern-gold/5 opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
                
                <span className="relative z-10 flex items-center gap-10">
                  Enter The Studio
                  <div className="relative">
                    <MoveRight className="w-4 h-4 group-hover:translate-x-6 transition-transform duration-1000 ease-in-out" />
                    <MoveRight className="w-4 h-4 absolute top-0 left-0 opacity-0 group-hover:opacity-40 group-hover:translate-x-3 transition-all duration-1000 delay-100 ease-in-out" />
                  </div>
                </span>
                
                <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-3/4 h-8 bg-govern-gold/15 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
              </button>

              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.3 }}
                transition={{ delay: 4, duration: 2 }}
                className="text-[9px] font-sans tracking-[0.3em] uppercase max-w-sm leading-relaxed"
              >
                Reserved for authorized administrative personnel only.
                <br />(MeitY Guideline Compliance V.2025)
              </motion.div>
            </motion.div>
          </AnimatePresence>
        </motion.div>

        {/* Vertical Rail Indicators */}
        <div className="absolute inset-y-0 left-12 flex flex-col justify-center gap-24 z-30 opacity-20 pointer-events-none">
          <div className="text-[8px] font-sans tracking-[0.6em] uppercase translate-x-[-50%] rotate-270 whitespace-nowrap">
            Foresight Framework
          </div>
          <div className="text-[8px] font-sans tracking-[0.6em] uppercase translate-x-[-50%] rotate-270 whitespace-nowrap">
            Scenario Engine 01
          </div>
        </div>
      </section>

      {/* Supporting Text Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center bg-govern-ink px-6 py-40 z-20 overflow-hidden">
        <div className="absolute inset-0 institutional-grid opacity-[0.05] pointer-events-none" />

        <motion.div 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          className="max-w-6xl text-center space-y-32"
        >
          <div className="relative inline-block px-12 py-24 bg-govern-forest/30 border border-govern-gold/10 rounded-sm backdrop-blur-sm border-debossed">
             <div className="absolute top-6 left-6 w-1 h-1 bg-govern-gold/20 rounded-full" />
             <div className="absolute top-6 right-6 w-1 h-1 bg-govern-gold/20 rounded-full" />
             <div className="absolute bottom-6 left-6 w-1 h-1 bg-govern-gold/20 rounded-full" />
             <div className="absolute bottom-6 right-6 w-1 h-1 bg-govern-gold/20 rounded-full" />

             <h2 className="font-serif text-3xl md:text-5xl text-govern-silk leading-[1.4] max-w-4xl mx-auto tracking-normal text-letterpress opacity-90 italic">
               &ldquo;A scenario-based simulator for AI governance practice in Indian public service.&rdquo;
             </h2>
             <div className="mt-16 flex items-center justify-center gap-6">
                <div className="h-px w-12 bg-govern-gold/20" />
                <span className="text-govern-gold/50 text-[10px] font-sans uppercase tracking-[0.8em] font-light">
                  Public Interest Infrastructure
                </span>
                <div className="h-px w-12 bg-govern-gold/20" />
             </div>
          </div>

          <div className="grid md:grid-cols-3 gap-16 text-left px-6">
            {[
              { 
                icon: FileText, 
                title: "Policy Resilience", 
                desc: "Stress-test governance strategies against high-stakes AI deployment variables." 
              },
              { 
                icon: Landmark, 
                title: "Institutional Core", 
                desc: "Scenarios designed around the specific administrative frictions of the Indian Secretariat." 
              },
              { 
                icon: ShieldCheck, 
                title: "Civic Integrity", 
                desc: "Modeling the tension between technological acceleration and the protection of fundamental rights." 
              }
            ].map((item, idx) => (
              <div key={idx} className="relative p-10 border border-govern-gold/5 bg-govern-charcoal/40 group hover:border-govern-gold/20 transition-all duration-700 overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-20 transition-opacity">
                  <item.icon className="w-16 h-16 text-govern-gold" strokeWidth={0.5} />
                </div>
                
                <div className="space-y-8 relative z-10">
                  <div className="flex items-center gap-5 text-govern-gold/40 group-hover:text-govern-gold transition-colors duration-1000">
                    <item.icon className="w-5 h-5" strokeWidth={1} />
                    <span className="font-sans text-[9px] tracking-[0.4em] uppercase font-bold">{item.title}</span>
                  </div>
                  <p className="text-govern-silk/40 font-serif text-xl leading-relaxed italic group-hover:text-govern-silk/60 transition-colors duration-1000">
                    {item.desc}
                  </p>
                  <div className="pt-4">
                    <div className="h-[1px] w-8 bg-govern-gold/30 group-hover:w-full transition-all duration-1000" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Institutional Footer */}
      <footer className="relative bg-[#050505] py-24 flex flex-col items-center justify-center px-12 border-t border-govern-gold/10 z-20 gap-16">
        <div className="flex flex-col md:flex-row items-center justify-between w-full max-w-7xl gap-12">
          <div className="flex items-center gap-10">
            <div className="text-[10px] font-sans tracking-[0.8em] uppercase text-govern-silk/20">
              GovernAI Studio &bull; MMXXVI
            </div>
            <div className="h-4 w-[1px] bg-govern-gold/10" />
            <div className="text-[8px] font-sans tracking-[0.4em] uppercase text-govern-silk/20">
              Implementation Node: 4.12
            </div>
          </div>
          
          <div className="text-[10px] font-sans tracking-[0.4em] uppercase text-govern-gold px-12 py-5 border border-govern-gold/20 rounded-sm flex items-center gap-8 bg-govern-forest/40 border-debossed backdrop-blur-sm">
            <ShieldCheck className="w-4 h-4 opacity-60" />
            Statutory Compliance: MeitY AI-G (2025)
          </div>
        </div>
        
        <div className="text-[9px] font-sans tracking-[0.3em] text-govern-silk/15 max-w-4xl text-center leading-[2.8] uppercase border-t border-govern-gold/5 pt-16">
          Access is strictly restricted to authorized administrative personnel. 
          The simulative models used herein are based on the 2025 India AI Governance Guidelines. 
          Unauthorized dissemination of architectural scenarios is prohibited.
        </div>
      </footer>
    </div>
  );
}

