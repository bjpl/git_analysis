import type { PageLoad } from './$types';

export interface PhilosophyPrinciple {
	id: string;
	title: string;
	description: string;
	icon: string;
	details: string[];
}

export interface TimelineEvent {
	id: string;
	date: string;
	title: string;
	company: string;
	location: string;
	type: 'work' | 'education' | 'achievement';
	description: string;
	technologies?: string[];
	achievements?: string[];
}

export interface Testimonial {
	id: string;
	name: string;
	title: string;
	company: string;
	avatar?: string;
	quote: string;
	rating: number;
	date: string;
}

export interface WorkPageData {
	philosophy: PhilosophyPrinciple[];
	timeline: TimelineEvent[];
	testimonials: Testimonial[];
	stats: {
		yearsExperience: number;
		projectsCompleted: number;
		clientsSatisfied: number;
		technologiesMastered: number;
	};
}

export const load: PageLoad<WorkPageData> = async () => {
	// Brandon's authentic teaching philosophy - 10 core principles
	const philosophy: PhilosophyPrinciple[] = [
		{
			id: '1',
			title: 'Situated & Ecological Learning',
			description: 'Language learning thrives in authentic, meaningful contexts that reflect real-world usage.',
			icon: 'globe',
			details: [
				'Connect language use to authentic cultural and social contexts',
				'Design activities that mirror real-world communication needs',
				'Integrate local community resources and authentic materials',
				'Foster understanding of language as a living, evolving system'
			]
		},
		{
			id: '2',
			title: 'Dialogic & Social Construction',
			description: 'Knowledge emerges through meaningful dialogue and collaborative interaction.',
			icon: 'message-circle',
			details: [
				'Prioritize interactive communication over passive reception',
				'Create opportunities for authentic peer-to-peer dialogue',
				'Build knowledge collectively through shared inquiry',
				'Value diverse perspectives and multilingual resources'
			]
		},
		{
			id: '3',
			title: 'Transformational Identity Development',
			description: 'Language learning transforms who we are, not just what we know.',
			icon: 'user',
			details: [
				'Support learners in developing multilingual identities',
				'Address identity conflicts and negotiate cultural boundaries',
				'Recognize language learning as personal transformation',
				'Honor learners\' linguistic and cultural backgrounds'
			]
		},
		{
			id: '4',
			title: 'Person-in-Context & Power Dynamics',
			description: 'Understanding learners within their social, cultural, and institutional contexts.',
			icon: 'users',
			details: [
				'Acknowledge institutional and social power structures',
				'Create inclusive spaces that value all linguistic backgrounds',
				'Address systemic barriers to language learning access',
				'Recognize intersectionality in learner experiences'
			]
		},
		{
			id: '5',
			title: 'Multi-Competence & Translingual Resources',
			description: 'Celebrating the full linguistic repertoire learners bring to the classroom.',
			icon: 'layers',
			details: [
				'Value translingual practices and code-switching',
				'Leverage learners\' full linguistic repertoires',
				'Move beyond monolingual bias in assessment',
				'Recognize multilingual competence as an asset'
			]
		},
		{
			id: '6',
			title: 'Communities of Practice & Socialization',
			description: 'Learning occurs through participation in meaningful communities.',
			icon: 'heart',
			details: [
				'Build classroom communities of practice',
				'Connect learners with target language communities',
				'Support legitimate peripheral participation',
				'Foster long-term engagement beyond the classroom'
			]
		},
		{
			id: '7',
			title: 'Emergent Motivation & Collaborative Construction',
			description: 'Motivation develops through meaningful engagement and shared goal construction.',
			icon: 'target',
			details: [
				'Co-construct learning goals with students',
				'Adapt instruction based on emergent interests',
				'Create intrinsically motivating learning experiences',
				'Support learner agency and autonomy'
			]
		},
		{
			id: '8',
			title: 'Assessment & Professional Development',
			description: 'Continuous growth through reflective practice and meaningful assessment.',
			icon: 'trending-up',
			details: [
				'Use formative assessment to guide instruction',
				'Engage in ongoing professional development',
				'Reflect critically on teaching practices',
				'Collaborate with colleagues for continuous improvement'
			]
		},
		{
			id: '9',
			title: 'Critical Consciousness & Institutional Awareness',
			description: 'Developing critical awareness of educational systems and social justice.',
			icon: 'eye',
			details: [
				'Examine institutional policies and their impacts',
				'Advocate for equitable language education practices',
				'Address issues of linguistic discrimination',
				'Promote social justice through language education'
			]
		},
		{
			id: '10',
			title: 'Complex Development & Integrated Skills',
			description: 'Language development is complex, non-linear, and multifaceted.',
			icon: 'zap',
			details: [
				'Integrate listening, speaking, reading, and writing skills',
				'Recognize non-linear development patterns',
				'Support diverse learning styles and preferences',
				'Embrace complexity in language acquisition processes'
			]
		}
	];

	const timeline: TimelineEvent[] = [
		{
			id: '1',
			date: '2019 - 2021',
			title: 'Content Designer & Language Educator',
			company: 'Immerse',
			location: 'Remote',
			type: 'work',
			description: 'Designed immersive VR language learning experiences and curriculum for Spanish language instruction.',
			technologies: ['Unity', 'VR Development', 'Curriculum Design', 'Assessment Tools'],
			achievements: [
				'Created engaging VR scenarios for authentic Spanish conversation practice',
				'Developed assessment rubrics aligned with ACTFL proficiency standards',
				'Collaborated with tech teams to optimize user experience for language learners'
			]
		},
		{
			id: '2',
			date: '2018 - 2019',
			title: 'Educational Technology Consultant',
			company: 'PartnerEd.tech',
			location: 'Remote',
			type: 'work',
			description: 'Provided consulting services for educational technology implementation in language learning contexts.',
			technologies: ['LMS Integration', 'Digital Assessment', 'EdTech Evaluation'],
			achievements: [
				'Helped schools integrate modern language learning technologies',
				'Trained educators on best practices for digital language instruction',
				'Evaluated and recommended EdTech solutions for diverse learning environments'
			]
		},
		{
			id: '3',
			date: '2016 - 2018',
			title: 'Graduate Student Instructor',
			company: 'UC Berkeley',
			location: 'Berkeley, CA',
			type: 'work',
			description: 'Teaching assistant and instructor for undergraduate Spanish language courses while pursuing MA-TESOL.',
			technologies: ['Canvas LMS', 'Language Lab Technology', 'Digital Portfolios'],
			achievements: [
				'Maintained 4.8/5.0 teaching evaluations across multiple semesters',
				'Developed innovative assessment methods using digital portfolios',
				'Mentored undergraduate students in academic and career development'
			]
		},
		{
			id: '4',
			date: '2014 - 2016',
			title: 'Online ESL Instructor',
			company: 'VIPKid',
			location: 'Remote',
			type: 'work',
			description: 'One-on-one English instruction to Chinese students aged 4-12 through interactive online platform.',
			technologies: ['Video Conferencing', 'Interactive Whiteboards', 'Gamification'],
			achievements: [
				'Taught over 1,000 online lessons with 98% positive feedback',
				'Adapted curriculum for diverse learning styles and cultural backgrounds',
				'Developed engaging activities for young language learners'
			]
		},
		{
			id: '5',
			date: '2013 - 2014',
			title: 'Spanish Instructor',
			company: 'Savannah College of Art and Design (SCAD)',
			location: 'Savannah, GA',
			type: 'work',
			description: 'Taught beginning and intermediate Spanish to art and design students.',
			achievements: [
				'Integrated creative arts projects with language learning objectives',
				'Developed culturally-rich curriculum connecting language and visual arts',
				'Supported students in study abroad preparation'
			]
		},
		{
			id: '6',
			date: '2012 - 2013',
			title: 'Spanish Teaching Assistant',
			company: 'Middlebury College',
			location: 'Middlebury, VT',
			type: 'work',
			description: 'Supported intensive Spanish instruction in prestigious summer language program.',
			achievements: [
				'Facilitated conversation groups and cultural activities',
				'Assisted with immersive Spanish-only environment maintenance',
				'Contributed to rigorous academic language program'
			]
		},
		{
			id: '7',
			date: '2018',
			title: 'MA-TESOL (Teaching English to Speakers of Other Languages)',
			company: 'UC Berkeley',
			location: 'Berkeley, CA',
			type: 'education',
			description: 'Advanced degree focusing on second language acquisition theory and pedagogical practice.',
			achievements: [
				'Specialized in technology-enhanced language learning',
				'Conducted research on multilingual identity development',
				'Completed comprehensive examination in SLA theory'
			]
		},
		{
			id: '8',
			date: '2011',
			title: 'BA in Spanish Language & Literature',
			company: 'Liberal Arts College',
			location: 'Southeast US',
			type: 'education',
			description: 'Undergraduate degree with study abroad experience and cultural immersion.',
			achievements: [
				'Study abroad in Spain and Latin America',
				'Senior thesis on contemporary Latin American literature',
				'Phi Beta Kappa academic honor society'
			]
		}
	];

	const testimonials: Testimonial[] = [
		{
			id: '1',
			name: 'Caitlin Williams',
			title: 'Director of Learning Experience',
			company: 'Immerse',
			quote: 'Brandon brings exceptional pedagogical expertise to educational technology. His deep understanding of language acquisition theory combined with practical teaching experience makes him invaluable in designing effective learning experiences.',
			rating: 5,
			date: '2021-03-15'
		},
		{
			id: '2',
			name: 'Misty Wilson',
			title: 'Senior Product Manager',
			company: 'EdTech Solutions',
			quote: 'Brandon\'s ability to bridge the gap between educational theory and practical implementation is remarkable. He consistently delivers curriculum that is both pedagogically sound and engaging for learners.',
			rating: 5,
			date: '2020-11-22'
		},
		{
			id: '3',
			name: 'Jennifer Peck',
			title: 'Graduate School Colleague',
			company: 'UC Berkeley',
			quote: 'Working with Brandon during our MA-TESOL program showed me his dedication to inclusive, equity-focused language education. His commitment to social justice in education is inspiring and authentic.',
			rating: 5,
			date: '2018-05-10'
		},
		{
			id: '4',
			name: 'Katie Dutcher',
			title: 'Language Program Coordinator',
			company: 'International Education Services',
			quote: 'Brandon\'s innovative approach to language instruction and his natural ability to connect with students from diverse backgrounds make him an exceptional educator. His students consistently show remarkable progress.',
			rating: 5,
			date: '2017-08-28'
		}
	];

	const stats = {
		yearsExperience: 10,
		projectsCompleted: 1000,
		clientsSatisfied: 500,
		technologiesMastered: 15
	};

	return {
		philosophy,
		timeline,
		testimonials,
		stats
	};
};