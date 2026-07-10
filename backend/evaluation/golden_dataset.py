"""
ArtikIQ Golden Evaluation Dataset
30 questions spanning all 15 chapters of "Human Communication Disorders"
(Anderson & Shames, 8th Edition).

Ground truth answers were written directly from real textbook content
(verified by reading the actual PDF page-by-page), not from general AI knowledge.

3 corrections were made after initial drafting, once live ArtikIQ answers
revealed the original ground truth was incomplete:
  - Question 7 (AAC model) — broadened to include both the 6-part and 3-part models
  - Question 8 (swallowing nerves) — broadened from 1 nerve to all 4 relevant nerves
  - Original "person-first language" question dropped (book didn't directly cover it),
    replaced with the NOMS question (Q9 here)
"""

GOLDEN_DATASET = [
    {
        "id": 1,
        "chapter": "Chapter 3: The Biology and Physics of Speech",
        "question": "What are the main places of articulation for consonant sounds in English?",
        "ground_truth": "The main places of articulation include bilabial (lips together, as in 'bay,' 'pay,' 'may'), labiodental (lower lip to upper teeth, as in 'van,' 'fan'), linguadental (tongue tip to upper teeth, as in 'this,' 'thin'), lingua-alveolar (tongue tip to the ridge behind the upper teeth, as in 'dip,' 'tip,' 'zip'), linguapalatal (tongue blade to hard palate, as in 'gin,' 'chin,' 'shin'), linguavelar (tongue back to hard or soft palate, as in 'gum,' 'come,' 'bag,' 'back'), and glottal (vocal folds, as in 'hay')."
    },
    {
        "id": 2,
        "chapter": "Chapter 7: Stuttering and Other Disorders of Fluency",
        "question": "How do fluency-shaping therapies differ from stuttering modification therapies?",
        "ground_truth": "Fluency-shaping therapies take a top-down approach, focusing on fine-tuning the mechanics of speech production rather than the emotional and cognitive components of stuttering. The goal is that as stuttered speech decreases and fluent talking time increases, the person's expectations shift from anticipating stuttering to anticipating fluency, reducing speech-related fears. Stuttering modification therapies take a bottom-up approach, targeting the maladaptive, distorted attitudes and thoughts underlying disfluent speech. This approach has clients confront feared situations and eliminate avoidance behaviors through strategies like voluntary stuttering and easy controlled stuttering, with the philosophy that decreasing fear and instilling control over speech will reduce stuttering."
    },
    {
        "id": 3,
        "chapter": "Chapter 8: Voice Disorders",
        "question": "What is hyperfunctional dysphonia and what causes it?",
        "ground_truth": "Hyperfunctional dysphonia refers to several forms of hoarseness associated with excessive closure of the glottis, occurring when the vocal folds are squeezed together so tightly that they cannot vibrate normally. Many cases result from overuse or misuse of the laryngeal mechanism, referred to as phonotrauma. The resulting voice may be quite hoarse and low-pitched."
    },
    {
        "id": 4,
        "chapter": "Chapter 9: Cleft Lip and Palate and Other Craniofacial Disorders",
        "question": "Why is a multidisciplinary team approach important for children with cleft lip and palate?",
        "ground_truth": "Children with craniofacial anomalies, including cleft lip and palate, often have multiple complex issues including feeding and nutritional problems, developmental delay, hearing loss, abnormal speech or resonance, dental and orthodontic abnormalities, and possible psychosocial problems. No single professional can address all these areas, so a team approach is recommended, including at minimum a plastic surgeon, dental professional, and speech-language pathologist, often supplemented by an oral surgeon, otolaryngologist, pediatrician, geneticist, psychologist, and audiologist."
    },
    {
        "id": 5,
        "chapter": "Chapter 14: Aphasia and Related Acquired Language Disorders",
        "question": "What are the key characteristics of Broca's aphasia?",
        "ground_truth": "Broca's aphasia is characterized by a paucity of speech, difficulties in word retrieval, and a labored, slow rate of speech. Individuals often omit small grammatical elements such as 'the,' 'is,' and 'on,' as well as word endings like '-ing,' '-s,' and '-ed' — a pattern called agrammatism. Comprehension of spoken and written language is notably better than spoken output would suggest. Writing is also impaired, partly because most patients also have right-arm and right-leg paralysis requiring them to learn to write with their left hand."
    },
    {
        "id": 6,
        "chapter": "Chapter 14: Aphasia and Related Acquired Language Disorders",
        "question": "How does fluent aphasia differ from Broca's aphasia in terms of speech production?",
        "ground_truth": "Fluent aphasias result from posterior brain damage, which does not affect the area of the brain responsible for initiating and producing speech. Patients with posterior lesions speak fluently, at rather normal rates, with patterns appropriate for their native language. However, many have difficulty with the input side of language, such as auditory and reading comprehension. This contrasts with Broca's aphasia (a nonfluent aphasia from anterior damage), where speech is labored and slow but comprehension is relatively preserved."
    },
    {
        "id": 7,
        "chapter": "Chapter 15: Augmentative and Alternative Communication",
        "question": "What is the AAC communication model and what does it include?",
        "ground_truth": "AAC can be viewed in terms of a broad communication model including six components: a sender with the intention of communicating, a receiver engaged in an interaction with the sender, a set or system of symbols to represent messages, a channel through which the message is sent, the broader context or environment in which the communication takes place, and complex feedback systems within and between individuals. AAC can also be modeled as a process composed of three core aspects: a means to represent a symbol, a means to select a symbol, and a means to transmit a message."
    },
    {
        "id": 8,
        "chapter": "Chapter 16: Disorders of Swallowing",
        "question": "What cranial nerves are involved in the oral preparatory and oral phases of swallowing, and what is their function?",
        "ground_truth": "Four cranial nerves are involved in the oral preparatory and oral phases of swallowing. The Trigeminal Nerve (V) provides sensation to the tongue and oral mucosa and motor control for the muscles of mastication. The Facial Nerve (VII) provides taste sensation to the anterior tongue and motor control for facial muscles and lip seal. The Glossopharyngeal Nerve (IX) provides taste to the posterior tongue and innervates the parotid gland, becoming active mainly during the oral phase. The Hypoglossal Nerve (XII) provides motor control for the tongue muscles, sealing the oral cavity, preparing the bolus, and moving it toward the pharynx."
    },
    {
        "id": 9,
        "chapter": "Chapter 1: Introduction",
        "question": "What is the role of the National Outcome Measurement System (NOMS) in speech-language pathology?",
        "ground_truth": "Since 1997, ASHA has been compiling objective, quantitative data examining the effectiveness of speech-language pathologists' work through the National Outcome Measurement System (NOMS). In 1998, ASHA established the National Center for Treatment Effectiveness in Communication Disorders as the adult health care component of NOMS. This research has shown that patients in inpatient rehabilitation facilities improve in functional communication as a result of speech-language pathology services, with improvement rates varying by disorder type — for example, 90 percent of patients with fluency disorders showed improvement, compared to 73 percent of patients with spoken language comprehension disorders."
    },
    {
        "id": 10,
        "chapter": "Chapter 1: Introduction",
        "question": "Approximately how many Americans have communication disorders, and what is the role of multidisciplinary teaming in serving them?",
        "ground_truth": "Approximately one out of eight to ten individuals, or 46 million Americans, has a communication disorder. These individuals can be of any age, race, gender, sexual orientation, language, ethnic, religious, occupational, and socioeconomic group. While audiologists and speech-language pathologists are independent, autonomous health professionals whose services don't require authorization by a physician, multidisciplinary teaming is an important part of clinical practice to ensure patients are treated holistically. In schools, this includes collaboration with parents, classroom teachers, reading teachers, learning disability teachers, counselors, school psychologists, and other specialists."
    },
    {
        "id": 11,
        "chapter": "Chapter 2: Development of Communication, Language, and Speech",
        "question": "What language milestones are typically expected by the time a child reaches fourth grade?",
        "ground_truth": "By fourth grade, the emphasis shifts from spoken to written language in both input and output, and the child uses reading skills to learn advanced, specialized vocabulary, figurative or nonliteral language, and complex grammatical forms. This shift to reading and writing requires greater metalinguistic competence, since written language is decontextualized and requires the user to obtain contextual information from print alone, making it more abstract. This corresponds with a developmental shift in cognition from concrete to abstract thinking."
    },
    {
        "id": 12,
        "chapter": "Chapter 4: Multicultural and Multilingual Considerations",
        "question": "What is the difference between simultaneous and successive bilingual language acquisition?",
        "ground_truth": "Simultaneous acquisition of two languages prior to age 3 may occur systematically without negative influence of one language upon the other. Successive acquisition occurs when an individual acquires a second language after the onset of development of the first language — for example, when one language is learned in the home and another at school. Learning a second language may also result in modified brain organization involving right brain mechanisms not typically involved in single-language learning."
    },
    {
        "id": 13,
        "chapter": "Chapter 5: Genetics",
        "question": "Why is genetics education important for speech-language pathologists?",
        "ground_truth": "Most, if not all, communication disorder conditions have a genetic link, although some linkages have not yet been identified. It is essential that students and practicing speech-language pathologists receive education about genetics and resources for connecting with genetics professionals, since they must apply this knowledge in translational research as well as in assessment and intervention strategies. Translational research involves applying laboratory findings to clinical settings, serving as a bridge between research and practice. Understanding genetics helps integrate this information into diagnosis, prevention, and treatment of communication disorders."
    },
    {
        "id": 14,
        "chapter": "Chapter 6: Articulatory and Phonological Disorders",
        "question": "What is the minimal pair (contrast) approach used in phonological intervention?",
        "ground_truth": "The minimal pair or contrast approach focuses on minimal word pairs that contrast in the target sound and the child's error pattern — for example, 'bow' and 'boat' for a child who deletes consonants at the ends of words. Perception and production activities are organized around sets of these contrasting pairs. Related activities, such as grouping or categorizing tasks that highlight phonological characteristics, can also be effective; Metaphon therapy formalizes this concept. Intervention research has demonstrated that both the minimal pair approach and the cycles approach are effective."
    },
    {
        "id": 15,
        "chapter": "Chapter 10: Neurogenic Disorders of Speech in Children and Adults",
        "question": "What are the three main categories of cerebral palsy based on movement disorder type?",
        "ground_truth": "Cerebral palsy can be classified into three main categories based on the type of movement disorder: spastic cerebral palsy (stiff and difficult movement), which accounts for 70-80% of cases and involves permanently contracted, stiff muscles; athetoid or dyskinetic cerebral palsy (involuntary and uncontrolled movement), characterized by slow, writhing movements that may also involve facial and articulator muscles, resulting in developmental dysarthria; and ataxic cerebral palsy. A fourth category may involve combinations of these types."
    },
    {
        "id": 16,
        "chapter": "Chapter 6: Articulatory and Phonological Disorders",
        "question": "What is the difference between an articulation disorder and a phonological disorder, based on where the deficit occurs in the speech production system?",
        "ground_truth": "The speech sound system can be divided into a phonetic level and phonological levels. The phonetic level involves audition-motor speech production and includes both perception (input) and production (output) components. Articulation disorders arise from deficiencies at this phonetic level — for example, from neurological impairments like dysarthria or apraxia, physical anomalies like cleft palate, or deficits in motor learning such as isolated sound distortions. Phonological disorders, by contrast, arise from the cognitive-linguistic components of the speech sound system — the representation and organization levels — reflecting deficits in the child's underlying knowledge of the sound system rather than purely motor or perceptual problems."
    },
    {
        "id": 17,
        "chapter": "Chapter 6: Articulatory and Phonological Disorders",
        "question": "What are some common phonological substitution processes seen in children, and can you give an example of each?",
        "ground_truth": "Common phonological substitution processes include: stopping (e.g., 'see' produced as [ti]), gliding (e.g., 'red' produced as [lɛd]), nasalization (e.g., 'bow' produced as [noʊ]), fronting (e.g., 'cow' produced as [taʊ]), backing (e.g., 'tea' produced as [ki]), neutralization (e.g., 'bye' produced as [bai]), denasalization (e.g., 'me' produced as [bi]), and glottal replacement (e.g., 'bike' produced as [bai?])."
    },
    {
        "id": 18,
        "chapter": "Chapter 17: Hearing and Hearing Disorders",
        "question": "How do audiologists use air-conduction and bone-conduction thresholds together to determine the type of hearing loss?",
        "ground_truth": "Air-conduction thresholds show the total amount of hearing loss present. Bone-conduction thresholds show the amount of hearing loss that is sensory/neural. In conductive hearing losses, the air-conduction thresholds are elevated while the bone-conduction thresholds remain normal, since the inner ear and pathways beyond are unaffected. In sensorineural hearing losses, the amount of hearing loss by air conduction is approximately the same as the amount of loss by bone conduction, since the damage is to the inner ear or auditory nerve, affecting both. By comparing the two, audiologists can determine if the loss is conductive, sensorineural, or a mix of both."
    },
    {
        "id": 19,
        "chapter": "Chapter 17: Hearing and Hearing Disorders",
        "question": "What is the difference between the Speech Recognition Threshold (SRT) and the Speech Detection Threshold (SDT)?",
        "ground_truth": "The Speech Recognition Threshold (SRT) is the point at which speech can barely be heard and understood about 50 percent of the time, with a normal range of -10 to 15 dB HL. The SRT typically approximates the pure-tone average of thresholds at 500, 1000, and 2000 Hz, making it a useful reliability check for pure-tone test results. The Speech Detection Threshold (SDT), also called the Speech Awareness Threshold (SAT), is the lowest level in decibels at which a person can barely detect the presence of speech and recognize it as speech, without necessarily understanding it. SDTs usually require about 5-10 dB less intensity than SRTs, though they are rarely measured today."
    },
    {
        "id": 20,
        "chapter": "Chapter 9: Cleft Lip and Palate and Other Craniofacial Disorders",
        "question": "Why are children with a history of cleft palate at greater risk for middle-ear disease compared to children with cleft lip only?",
        "ground_truth": "The tensor veli palatini muscle, which opens the eustachian tube during swallowing and yawning, originates in the velum (soft palate). If there is or has been a cleft in that area, this muscle may not function properly, preventing the eustachian tube from opening. This means negative pressure is not released and fluid accumulates in the middle ear (middle-ear effusion), which can lead to infection (otitis media). Chronic middle-ear effusion and otitis media can cause conductive hearing loss and delay speech and language development. Children with cleft lip only do not have this same risk, since the velum and its muscles are not affected."
    },
    {
        "id": 21,
        "chapter": "Chapter 9: Cleft Lip and Palate and Other Craniofacial Disorders",
        "question": "What is the difference between an overt submucous cleft and an occult submucous cleft?",
        "ground_truth": "A submucous cleft palate is a congenital defect affecting the underlying structure of the palate while the oral surface mucosa remains intact. An overt submucous cleft can be identified through an intra-oral examination, with the most common sign being a bifid or hypoplastic uvula; a zona pellucida (a thin, dark or bluish area in the velum caused by separation of the muscles) may also be visible. An occult submucous cleft, meaning 'hidden,' is a defect in the velum that is not apparent on the oral surface at all. It can only be detected by viewing the nasal surface of the velum through nasopharyngoscopy or surgical dissection, and typically goes undetected unless hypernasal speech prompts an evaluation."
    },
    {
        "id": 22,
        "chapter": "Chapter 18: Audiologic Rehabilitation",
        "question": "How does an induction loop system work to help people with hearing loss?",
        "ground_truth": "An induction loop system consists of a microphone connected via hardwire or FM transmitter to an amplifier, which connects to a loop of wire encircling the room or seating area (a personal induction loop wire can also be worn around the listener's neck). An electrical current flows through the loop, creating a magnetic field that can be picked up by hearing aids equipped with telecoils. The hearing aid user simply sets their hearing aid to the telecoil setting to pick up the magnetic signal instead of relying on the acoustic signal from the microphone."
    },
    {
        "id": 23,
        "chapter": "Chapter 18: Audiologic Rehabilitation",
        "question": "What is the difference between the Speech Perception in Noise (SPIN) test and the Hearing in Noise Test (HINT)?",
        "ground_truth": "Both are objective outcome measures used to assess speech perception in adults aged 18 and older. The Speech Perception in Noise (SPIN) test uses 8 sets of 50 sentences to measure speech perception specifically when listening in noisy conditions. The Hearing in Noise Test (HINT) uses 25 lists of 10 sentences to measure sentence speech reception thresholds in both quiet and noisy environments."
    },
    {
        "id": 24,
        "chapter": "Chapter 5: Genetics",
        "question": "What is the Human Genome Project and why is it significant for speech-language pathology?",
        "ground_truth": "The Human Genome Project (HGP) began in the United States in 1990, when the National Institutes of Health and the Department of Energy joined forces with international partners to decipher the massive amount of information contained in human genomes. The HGP is credited with mapping the human genome, opening doors for research into the genetic basis of many conditions. Since rapid advances in medical genetics continue to identify the role of genetics in communication development and disorders, speech-language pathologists and audiologists need to be aware of these advances to engage in competent service delivery to individuals and families."
    },
    {
        "id": 25,
        "chapter": "Chapter 2: Development of Communication, Language, and Speech",
        "question": "What is the relationship between word comprehension and word production in toddlers?",
        "ground_truth": "Most words are learned receptively (comprehension) and then produced expressively (production) by toddlers, though some words may be learned directly in production when context makes the word's meaning obvious. Comprehension tends to precede production for words usable in multiple contexts, such as 'want' or 'no,' but this isn't the case for words usable in only one context, such as 'bye-bye.' This comprehension-production relationship is dynamic and changes with the child's developmental level."
    },
    {
        "id": 26,
        "chapter": "Chapter 4: Multicultural and Multilingual Considerations",
        "question": "How does Spanish influence affect the use of forms of 'to be' and pronouns in English, according to dialect research?",
        "ground_truth": "Spanish influence on English syntax can result in the absence of forms of 'to be' in the present progressive tense, such as saying 'He getting hungry' instead of 'He is getting hungry.' Pronouns may also be absent as subjects of sentences when the subject is already obvious from a preceding sentence — for example, 'Carol left yesterday. I think is coming back tomorrow' instead of 'I think she is coming back tomorrow.'"
    },
    {
        "id": 27,
        "chapter": "Chapter 10: Neurogenic Disorders of Speech in Children and Adults",
        "question": "How does bilateral vagus nerve damage differ from unilateral damage in terms of voice and speech symptoms?",
        "ground_truth": "With unilateral vagus nerve lesions, the vocal cord on the affected side is paralyzed, leading to flaccid dysphonia with moderate breathiness, harshness, and reduced volume, along with possible diplophonia, short phrases, and inhalatory stridor. The soft palate on that same side is also paralyzed, causing hypernasality. With bilateral lesions, the vocal cords on both sides are paralyzed and elevation of the soft palate is impaired on both sides, resulting in more severe breathiness and hypernasality, audible inhalation, and other more pronounced symptoms compared to unilateral damage."
    },
    {
        "id": 28,
        "chapter": "Chapter 10: Neurogenic Disorders of Speech in Children and Adults",
        "question": "What is the difference between unilateral and bilateral hypoglossal nerve lesions in terms of articulatory effects?",
        "ground_truth": "With unilateral hypoglossal lesions affecting linguo-palatal consonants, patients typically learn to compensate rapidly for the unilateral tongue weakness or paralysis. Bilateral hypoglossal lesions are associated with more severe articulatory disturbances. In these cases, tongue movement may be severely restricted, and speech sounds requiring elevation of the tongue tip to the upper alveolar ridge or hard palate — such as /t/, /d/, /n/, and /l/, along with high front vowels — may be grossly distorted."
    },
    {
        "id": 29,
        "chapter": "Chapter 7: Stuttering and Other Disorders of Fluency",
        "question": "According to neuropsycholinguistic theories, what causes stuttering to occur during speech production?",
        "ground_truth": "One neuropsycholinguistic theory holds that fluent speech production requires two components — a linguistic/symbol system and a paralinguistic/signal system — which are processed separately in the brain before converging into a common output system. If these two components are not synchronously timed, a breakdown in fluency results; this breakdown is experienced as true stuttering only when 'time pressure' is also present. A separate theory proposes that stuttering stems from a disturbed interaction between phonological encoding and verbal self-monitoring, where the monitoring system falsely detects 'errors' and attempts to self-correct by halting or stalling ongoing speech, resulting in stuttering."
    },
    {
        "id": 30,
        "chapter": "Chapter 7: Stuttering and Other Disorders of Fluency",
        "question": "What was the diagnosogenic-semantogenic theory of stuttering, and during what time period was it influential?",
        "ground_truth": "The diagnosogenic-semantogenic theory, developed by Wendell Johnson, was perhaps the most widely embraced theory of the cause of stuttering from 1940 through 1970."
    },
]
