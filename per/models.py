import uuid
from api.models import Country
from django.db import models
from django.conf import settings
from django.utils import timezone
from enumfields import EnumIntegerField
from enumfields import IntEnum
from tinymce import HTMLField
from deployments.models import ERUType
from api.storage import AzureStorage

# Write model properties to dictionary
def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values())
        else:
            data[f.name] = f.value_from_object(instance)
    return data

class ProcessPhase(IntEnum):
    BASELINE = 0
    ORIENTATION = 1
    ASSESSMENT = 2
    PRIORITIZATION = 3
    PLAN_OF_ACTION = 4
    ACTION_AND_ACCOUNTABILITY = 5

class NSPhase(models.Model):
    """ NS PER Process Phase """
    country = models.OneToOneField(Country, on_delete=models.CASCADE, default=1 ) #default=1 needed only for the migration, can be deleted later
    phase = EnumIntegerField(ProcessPhase, default=ProcessPhase.BASELINE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('updated_at', 'country', )
        verbose_name = 'NS PER Process Phase'
        verbose_name_plural = 'NS-es PER Process Phase'

    def __str__(self):
        if self.country is None:
            name = None
        else:
            name = self.country.society_name
        return '%s (%s)' % (name, self.phase)

class Status(IntEnum):
    NO                          = 0
    YES                         = 1
    NOT_REVIEWED                = 2 # Not Reviewed     
    DOES_NOT_EXIST              = 3 # Does not exist
    PARTIALLY_EXISTS            = 4 # Partially exists
    NEED_IMPROVEMENTS           = 5 # Need improvements
    EXIST_COULD_BE_STRENGTHENED = 6 # Exist, could be strengthened
    HIGH_PERFORMANCE            = 7 # High Performance

class Language(IntEnum):
    SPANISH = 0
    FRENCH =  1
    ENGLISH = 2

class Draft(models.Model):
    """ PER draft form header """
    code = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    data = models.TextField(null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ('code', 'created_at')
        verbose_name = 'Draft Form'
        verbose_name_plural = 'Draft Forms'

    def __str__(self):
        if self.country is None:
            country = None
        else:
            country = self.country.society_name
        return '%s - %s (%s)' % (self.code, self.user, country)

class Form(models.Model):
    """ PER form header """
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    language = EnumIntegerField(Language)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    ns = models.CharField(max_length=100, null=True, blank=True) # redundant, because country has defined ns – later in "more ns/country" case it can be useful.
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(default=timezone.now)
    finalized = models.BooleanField(default=False)
    validated = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(default='192.168.0.1')
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    comment = models.TextField(null=True, blank=True) # form level comment

    class Meta:
        ordering = ('code', 'name', 'language', 'created_at')
        verbose_name = 'Form'
        verbose_name_plural = 'Forms'

    def __str__(self):
        if self.country is None:
            name = None
        else:
            name = self.country.society_name
        return '%s - %s (%s, %s)' % (self.code, self.name, self.language, name)

def question_details(question_id, code):
    q = code + question_id
    # Do not edit it manually. It is generated from frontend files (PER/form_inputIds and form_questions_to_python) via shell scripts:
    if q == 'a1c0q0' : return '1.1 NS establishes its auxiliary role to the public authorities through a clear mandate and roles set out in applicable legislation policies and plans.'
    elif q == 'a1c0q1' : return '1.2 NS mandate is aligned with RCRC Fundamental Principles.'
    elif q == 'a1c0q2' : return '1.3 NS mandate is reflected in policy strategy plans and procedures. The mandate is disseminated and understood by staff and volunteers.'
    elif q == 'a1c0q3' : return '1.4 NS promotes IHL to the public authorities and uses humanitarian diplomacy to promote compliance.'
    elif q == 'a1c0q4' : return 'Component 1 performance'
    elif q == 'a1c1q0' : return '2.1 NS DRM strategy reflects the NS mandate analysis of country context trends operational objectives success indicators.'
    elif q == 'a1c1q1' : return '2.2 NS DRM strategy is regularly reviewed reflected in response plan and known by staff and volunteers.'
    elif q == 'a1c1q2' : return '2.3 NS DRM strategy includes clear engagement with technical sectors and support services to ensure comprehensive response.'
    elif q == 'a1c1q3' : return 'Component 2 performance'
    elif q == 'a1c2q0' : return '3.1 NS has its own DRM policy or has adopted the IFRC policy.'
    elif q == 'a1c2q1' : return '3.2 DRM policy sets out guiding principles and values that guide decision-making on the response approach and actions.'
    elif q == 'a1c2q2' : return '3.3 DRM policy is inclusive and involves other relevant sectors and services.'
    elif q == 'a1c2q3' : return '3.4 DRM policy is reflected in response plans procedures and it is adhered to by staff and volunteers.'
    elif q == 'a1c2q4' : return 'Component 3 performance'
    elif q == 'a1c3q0' : return '4.1 NS has an IDRL humanitarian diplomacy plan /actions in place based on IFRC\'s IDRL Checklist.'
    elif q == 'a1c3q1' : return '4.2 NS has identified the relevant legal facilities (i.e. special entitlements and exemptions) in the national legislation.'
    elif q == 'a1c3q2' : return '4.3 NS has staff trained in IDRL & IHL to act as a focal point in an emergency.'
    elif q == 'a1c3q3' : return '4.4 NS is advocating the government to enact legislation in line with the Model Act for the Facilitation and Regulation of International Disaster Relief and Initial Recovery Assistance.'
    elif q == 'a1c3q4' : return '4.5 NS tests and/or tracks IDRL lessons through response operations to guide its future humanitarian diplomacy work.'
    elif q == 'a1c3q5' : return 'Component 4 performance'
    elif q == 'a1c4q0' : return '5.1 NS has mechanisms in place to ensure the affected populations are involved in all stages of the response (including decision making) to ensure assistance is appropriate and meets their needs and priorities.'
    elif q == 'a1c4q1' : return '5.2 NS has trained CEA focal points at key branches and headquarters.'
    elif q == 'a1c4q2' : return '5.3 A NS CEA plan is developed and implemented standard templates are available and procedures are included in SOPs.'
    elif q == 'a1c4q3' : return '5.4 Safe and accessible feedback and complaints mechanisms exists to record refer or respond and monitor communities\' concerns and requests regarding the assistance provided or protection issues (including for sexual exploitation and abuse).'
    elif q == 'a1c4q4' : return '5.5 NS has adopted the Protection for sexual exploitation and abuse policy in line with the International conference resolution on Sexual and Gender Based Violence.'
    elif q == 'a1c4q5' : return '5.6 NS adheres to Sphere and the Core Humanitarian Standards (may consider IASC Guidelines for Integrating gender based violence interventions IASC Guidelines on Including persons with disabilities in humanitarian action) and integrates them into sectorial activities during assessment planning and response.'
    elif q == 'a1c4q6' : return '5.7 NS adheres to protection policies to support their protection services (safe spaces for child protection actions for unaccompanied and separated children prevention of sexual and gender-based violence violence prevention psychosocial support restoring family links accessibility of facilities and information) to respond.'
    elif q == 'a1c4q7' : return '5.8 NS plans and procedures actively minimise potential harmful social economic and environmental impacts of assistance (do no harm principle).'
    elif q == 'a1c4q8' : return '5.9 NS follows the Minimum Standards for Protection Gender and Inclusion in Emergencies.'
    elif q == 'a1c4q9' : return 'Component 5 performance'
    elif q == 'a2c0q0' : return '6.1 A risk monitoring system (including a focal point) is formally established and linked to preparedness and early action.'
    elif q == 'a2c0q1' : return '6.2 NS has the capacity to collect and analyse primary and secondary data (including sectorial specific information) on emerging political social and economic trends that could influence humanitarian action.'
    elif q == 'a2c0q2' : return '6.3 The current/likely gaps barriers risks and challenges to NS acceptance security and access have been identified.'
    elif q == 'a2c0q3' : return '6.4 Early warning system is established and includes thresholds (including for slow on-set disasters) and required mechanisms to communicate and activate early action.'
    elif q == 'a2c0q4' : return '6.5 Updated national multi-hazard risk analysis and maps (including changing risks patterns) are shared with all branches at least once every 2 years.'
    elif q == 'a2c0q5' : return '6.6 Communities and local volunteers contribute to the regular update of the multi-hazard risk mapping and Vulnerability and capacity assessments (VCA).'
    elif q == 'a2c0q6' : return '6.7 Risk assessments at community level include the analysis of the potential connectors and dividers within a community.'
    elif q == 'a2c0q7' : return '6.8 For at-risk areas primary and secondary data on vulnerabilities and capacities of communities is broken down by age gender disability income and other context-specific diversity and cultural factors and include potential protection-related consequences on affected populations.'
    elif q == 'a2c0q8' : return '6.9 For cross-border high risk areas NSs coordinate risk monitoring are familiar with each other\'s capacities and procedures and have a mechanism in place to share information.'
    elif q == 'a2c0q9' : return 'Component 6 performance'
    elif q == 'a2c1q0' : return '7.1 Analysis of scenarios is multi-sectorial (e.g. health livelihood protection) and includes identification of drivers (root causes of risks) and assumptions to inform potential impact.'
    elif q == 'a2c1q1' : return '7.2 NS has developed humanitarian scenarios for each high-risk area in the country and contingency plans are aligned with those of the public authorities.'
    elif q == 'a2c1q2' : return '7.3 A response strategy is available for each scenario and branches are involved in development of the response strategy affecting their area.'
    elif q == 'a2c1q3' : return '7.4 Scenarios include the identification of challenges to NS acceptance security and access during humanitarian operations.'
    elif q == 'a2c1q4' : return '7.5 Contingency plans include triggers to activate the plan especially for protracted and slow onset crises.'
    elif q == 'a2c1q5' : return '7.6 Contingency plans for potential regional crises include coordination mechanisms between neighbouring countries particularly for potential epidemic and pandemic crises.'
    elif q == 'a2c1q6' : return '7.7 Contingency plans for high risks are developed and reviewed on an annual basis.'
    elif q == 'a2c1q7' : return 'Component 7 performance'
    elif q == 'a2c2q0' : return '8.1 Responsibility for risk management is assigned to a trained staff within the NS and overall accountability for risk management is identified.'
    elif q == 'a2c2q1' : return '8.2 NS systematically identifies evaluates and mitigates any potential operational and reputational risks including risks of responding in insecure contexts.'
    elif q == 'a2c2q2' : return '8.3 Risk management is done holistically across technical sectors with mitigation measures identified and operationalised.'
    elif q == 'a2c2q3' : return '8.4 NS identifies key stakeholders and develops engagement strategies to increase acceptance by them.'
    elif q == 'a2c2q4' : return '8.5 Systems and procedures are in place to prevent fraud and corruption and reinforce acceptance security and access.'
    elif q == 'a2c2q5' : return '8.6 Reputational and integrity risk management is a standing item on the NS\'s Governing Board meetings.'
    elif q == 'a2c2q6' : return '8.7 NS has a crisis management unit/function to manage critical incidents.'
    elif q == 'a2c2q7' : return 'Component 8 performance'
    elif q == 'a2c3q0' : return '9.1 NS has a nominated trained focal point for disaster preparedness.'
    elif q == 'a2c3q1' : return '9.2 Preparedness gaps are identified based on risk analysis and response strategy and take into account the strengthening of support units.'
    elif q == 'a2c3q2' : return '9.3 Remedial actions for preparedness gaps are being implemented.'
    elif q == 'a2c3q3' : return '9.4 Financial gaps for preparedness and early actions are identified and resource mobilisation strategy is in place.'
    elif q == 'a2c3q4' : return '9.5 Preparedness actions are updated at least every two years and revised every six months or after every major disaster.'
    elif q == 'a2c3q5' : return '9.6 Policies and procedures exist to allocate emergency or development budgets for preparedness capacity strengthening.'
    elif q == 'a2c3q6' : return 'Component 9 performance'
    elif q == 'a2c4q0' : return '10.1 NS has an up-to-date approved business continuity plan for major emergency/crisis situation that would affect its ability to operate.'
    elif q == 'a2c4q1' : return '10.2 NS has an up-to-date approved procedure in place to communicate with donors to repurpose funds for unexpected or emerging needs.'
    elif q == 'a2c4q2' : return 'Component 10 performance'
    elif q == 'a2c5q0' : return '11.1 NS has up-to-date approved SOPs for all specific areas of intervention and support services to respond to disasters and crises.'
    elif q == 'a2c5q1' : return '11.2 SOPs have been disseminated to well-known and followed by staff and volunteers.'
    elif q == 'a2c5q2' : return '11.3 SOPs describe the roles and responsibilities of responders at strategic management and operational levels at HQ branches and communities.'
    elif q == 'a2c5q3' : return '11.4 SOPs incorporate procedures for all phases of response (early warning early action emergency assessment response planning etc.) including standardised templates.'
    elif q == 'a2c5q4' : return '11.5 SOPs include procedures to scale alert levels up and down.'
    elif q == 'a2c5q5' : return '11.6 Up-to-date and approved SOPs to respond to disasters and crises exist at branch level.'
    elif q == 'a2c5q6' : return '11.7 SOPs include a decision making flowchart which assigns decision making responsibility accordingly at each level.'
    elif q == 'a2c5q7' : return '11.8 SOPs include an up-to-date organogram with contact details.'
    elif q == 'a2c5q8' : return 'Component 11 performance'
    elif q == 'a2c6q0' : return '12.1 NS has an up-to-date approved multi-sectorial response plan for rapid deployment and efficient use of human and material resources.'
    elif q == 'a2c6q1' : return '12.2 The plan takes into consideration gender age disability and diversity complexities and community capacities.'
    elif q == 'a2c6q2' : return '12.3 The plan is developed by the NS with the participation of community staff volunteers governance management and technical inputs from IFRC where relevant.'
    elif q == 'a2c6q3' : return '12.4 The plan adheres to the Principles and Rules DRM policy and Fundamental principles.'
    elif q == 'a2c6q4' : return '12.5 The plan aligns with IFRC global standards and templates (EPOA).'
    elif q == 'a2c6q5' : return '12.6 The plan considers how to reduce and address secondary risks and is in line with the medium to longer term interventions focused on recovery.'
    elif q == 'a2c6q6' : return '12.7 The plan acknowledges response and recovery actions of other actors and is disseminated to the Movement and other relevant external actors.'
    elif q == 'a2c6q7' : return '12.8 NS has a process to adapt the plan to changing context and emergency needs.'
    elif q == 'a2c6q8' : return '12.9 NS can manage the transition from relief phase and use of short-term resources and volunteers to medium-term recovery interventions.'
    elif q == 'a2c6q9' : return '12.10 The plan is updated with lessons learned from real time and simulated exercises.'
    elif q == 'a2c6q10' : return '12.11 NS can manage the transition from relief phase and use of short-term resources and volunteers to medium-term recovery interventions.'
    elif q == 'a2c6q11' : return '12.12 NS has a process to develop and approve donation protocols that communicate priority needs to the public in times of disaster and crisis.'
    elif q == 'a2c6q12' : return 'Component 12 performance'
    elif q == 'a2c7q0' : return '13.1 Pre-disaster meetings with key stakeholders take place (at least once a year).'
    elif q == 'a2c7q1' : return '13.2 Key staff are familiar with pre-disaster/crisis agreements and how to operationalize them in a response.'
    elif q == 'a2c7q2' : return '13.3 Coordination and management arrangements with relevant local and national key actors are formalized (NGO INGO UN public authorities).'
    elif q == 'a2c7q3' : return '13.4 NS has an up-to-date capacity mapping of Movement partners.'
    elif q == 'a2c7q4' : return '13.5 Movement coordination agreements are known and available within NS and shared with IFRC.'
    elif q == 'a2c7q5' : return '13.6 All contractors have signed the Code of Conduct.'
    elif q == 'a2c7q6' : return '13.7 All pre-disaster agreements are in line with NS policies and procedures including Principles and Rules Strengthening Movement Coordination and Cooperation (SMCC) and in line with Quality and Accountability standards.'
    elif q == 'a2c7q7' : return '13.8 Agreements exist with public authorities to facilitate expedited import of humanitarian aid and visas for incoming personnel.'
    elif q == 'a2c7q8' : return '13.9 Agreements with key suppliers of goods and services are formalized and agreed with an agreed mechanism for activation.'
    elif q == 'a2c7q9' : return '13.10 Agreements with money transfer providers are formalised with an agreed mechanism for activation.'
    elif q == 'a2c7q10' : return '13.11 Agreements with existing Social Protection systems are in place to facilitate access to pre-existing databases of vulnerable populations.'
    elif q == 'a2c7q11' : return 'Component 13 performance'
    elif q == 'a3c0q0' : return '15.1 A focal point is identified and available for each NS specific area of intervention and services to provide technical guidance and support.'
    elif q == 'a3c0q1' : return '15.2 Staff and volunteers are trained and kept up to date in the specific areas of intervention and services.'
    elif q == 'a3c0q2' : return '15.3 Response materials and equipment database is up to date and gaps are noted and being addressed.'
    elif q == 'a3c0q3' : return '15.4 Resources (HR and equipment) are available and sufficient to cover the initial response needs.'
    elif q == 'a3c0q4' : return '15.5 Capacities are mapped in line with the different levels of response (Green - Yellow - Red).'
    elif q == 'a3c0q5' : return '15.6 Mechanisms are in place to share resources amongst branches/regions and with sister NSs.'
    elif q == 'a3c0q6' : return 'Component 15 performance'
    elif q == 'a3c1q0' : return '16.1 NS\'s early warning early action system - inclusive of Forecast-based Financing and disease surveillance - is an integral and accepted part of the national Early Warning Early Action strategies and preparedness system.'
    elif q == 'a3c1q1' : return '16.2 NS has a clear methodology to decide when and where early action should be taken based on a combination of vulnerability exposure and triggers.'
    elif q == 'a3c1q2' : return '16.3 NS has mechanisms to anticipate and respond to major hazards in coordination with the national system.'
    elif q == 'a3c1q3' : return '16.4 NS tests and makes use of new technologies appropriate for the context and audiences for sending alert messages related to early action (e.'
    elif q == 'a3c1q4' : return '16.5 NS has procedures and personnel permanently available to communicate alerts and initiate early action to all levels of the N'
    elif q == 'a3c1q5' : return '16.6 Branches have functioning local networks to inform communities of potential threats and activate early action (respecting mandates of public authorities).'
    elif q == 'a3c1q6' : return 'Component 16 performance'
    elif q == 'a3c2q0' : return '17.1 NS has a CBI preparedness plan properly budgeted and resourced with clear activities and outputs based on analysis and discussion with key stakeholders.'
    elif q == 'a3c2q1' : return '17.2 CBI preparedness plan is tailored to address NS opportunities and barriers to be ready to provide scalable emergency CBI.'
    elif q == 'a3c2q2' : return '17.3 NS has an up-to-date database of CBI trained and experienced staff and volunteers at headquarter and branch levels across sectors and support services to implement CBI within the response cycle.'
    elif q == 'a3c2q3' : return '17.4 NS has pre-disaster feasibility cash analysis and baseline about market systems prices and seasonality mapping of other actors and coordination structures.'
    elif q == 'a3c2q4' : return '17.5 NS has regularly revised CBI SOPs with clear roles and responsibilities outlined at each stage of the response process based on lessons learned from previous responses.'
    elif q == 'a3c2q5' : return '17.6 NS has mapped CBI delivery mechanisms service providers and has in place agreements including activation mechanism with money transfer providers.'
    elif q == 'a3c2q6' : return '17.7 NS has an up-to-date approved CBI toolkit that adapts CiE tools to the NS specific contexts.'
    elif q == 'a3c2q7' : return '17.8 NS routinely uses the CBI toolkit which is revised and updated based on feedback from preparedness and response actions.'
    elif q == 'a3c2q8' : return '17.9 NS leads CBI coordination mechanism both internally within the Movement and externally with other CBI actors in the country (public authorities UN NGOs etc...).'
    elif q == 'a3c2q9' : return 'Component 17 performance'
    elif q == 'a3c3q0' : return '18.1 NS has standardised templates used for primary and secondary data collection and reporting.'
    elif q == 'a3c3q1' : return '18.2 NS has a trained multi-sectorial emergency assessment team available to deploy in a timely manner.'
    elif q == 'a3c3q2' : return '18.3 NS emergency plans of actions are based on emergency needs assessment results.'
    elif q == 'a3c3q3' : return '18.4 Information is disaggregated according to gender age groups and others.'
    elif q == 'a3c3q4' : return '18.5 Emergency needs assessment analyses accessibility availability quality use and awareness of goods and services.'
    elif q == 'a3c3q5' : return '18.6 Emergency needs assessment takes into consideration existing capacities and analyses the national and international capacities responses and gaps.'
    elif q == 'a3c3q6' : return '18.7 Emergency needs assessment should analyse secondary risk specific needs/concerns of vulnerable people/coping mechanisms/early and self-recovery.'
    elif q == 'a3c3q7' : return 'Component 18 performance'
    elif q == 'a3c4q0' : return '19.1 NS communicates selection criteria to the affected population using preferred communication channels and involves community leaders/representatives.'
    elif q == 'a3c4q1' : return '19.2 NS identifies appropriate selection criteria based on existing vulnerability and taking into consideration gender diversity age and disabilities.'
    elif q == 'a3c4q2' : return '19.3 NS protects data collected from affected population.'
    elif q == 'a3c4q3' : return '19.4 Responders have been trained in data collection including the standardised templates.'
    elif q == 'a3c4q4' : return '19.5 NS cross-checks affected populations\' lists with community leaders other agencies authority etc… to verify inclusion/exclusion issues (considering protection of sensitive data).'
    elif q == 'a3c4q5' : return 'Component 19 performance'
    elif q == 'a3c5q0' : return '20.1 NS has a formally appointed focal point for EOC.'
    elif q == 'a3c5q1' : return '20.2 NS has up-to-date EOC SOPs which are consistent with other NS documents including sectors and support services.'
    elif q == 'a3c5q2' : return '20.3 EOC is activated according to defined response levels and activation is communicated.'
    elif q == 'a3c5q3' : return '20.4 Relevant staff and volunteers know their roles and responsibilities and are trained on SOPs.'
    elif q == 'a3c5q4' : return '20.5 All technical sectors and support services have procedures that integrate with the EOC SOPs.'
    elif q == 'a3c5q5' : return '20.6 EOC has intended space with sufficient equipment to manage information and coordination that does not affect other NS activities.'
    elif q == 'a3c5q6' : return '20.7 EOC facilities are self-sufficient with at least power water and telecommunications with functioning back-up means.'
    elif q == 'a3c5q7' : return '20.8 NS has an alternative location if the EOC space is not accessible.'
    elif q == 'a3c5q8' : return '20.9 NS has full and updated contact details for relevant personnel.'
    elif q == 'a3c5q9' : return '20.10 NS has legal access and use of designated emergency frequencies which link with other stakeholders in response.'
    elif q == 'a3c5q10' : return '20.11 EOC staff manages and displays regular updated information (maps operational details etc...).'
    elif q == 'a3c5q11' : return '20.12 Strategic decisions are made based on the situational analysis to address operational gaps and needs.'
    elif q == 'a3c5q12' : return '20.13 Clear levels of authority exist between the strategic and management levels of the EOC.'
    elif q == 'a3c5q13' : return '20.14 EOC is operational 24/7 however operational period of staff does not exceed 12 hrs/shift.'
    elif q == 'a3c5q14' : return '20.15 Information is collected validated and analyzed to provide updated standardized situation reports.'
    elif q == 'a3c5q15' : return 'Component 20 performance'
    elif q == 'a3c6q0' : return '21.1 Key staff at headquarters and branch level are familiar with IM templates (from NS or IFRC) methodology and procedures.'
    elif q == 'a3c6q1' : return '21.2 NS has access to equipment to compile visualise and share information (e.g. printers cartridges scanners and battery powered projectors).'
    elif q == 'a3c6q2' : return '21.3 NS has a system to store and share files with emergency personnel.'
    elif q == 'a3c6q3' : return '21.4 NS has access to updated data on high-risk areas (demographic socio-economic) disaggregated by age gender and disability.'
    elif q == 'a3c6q4' : return '21.5 Information and specifically decisions are documented and filed.'
    elif q == 'a3c6q5' : return '21.6 NS has a standardised Situation Report format that includes information on situation NS response other actors\' response challenges achievements and gaps.'
    elif q == 'a3c6q6' : return '21.7 The Situation Reports are analysed to adapt response plans.'
    elif q == 'a3c6q7' : return '21.8 NS has mechanisms to share information across levels sectors and support services.'
    elif q == 'a3c6q8' : return 'Component 21 performance'
    elif q == 'a3c7q0' : return '22.1 NS regularly tests its early action and response system through simulation and drills.'
    elif q == 'a3c7q1' : return '22.2 Lessons drawn from drills simulations and responses inform revisions in the emergency procedures.'
    elif q == 'a3c7q2' : return '22.3 NS includes access acceptance security and the practical application of the Fundamental Principles in their simulations and drills.'
    elif q == 'a3c7q3' : return '22.4 Branches in high-risk areas test their response system including early action through drills and simulations.'
    elif q == 'a3c7q4' : return '22.5 Testing includes issues of safe access (access perception acceptance and security).'
    elif q == 'a3c7q5' : return '22.6 NS conducts cross-border simulations in relevant contexts.'
    elif q == 'a3c7q6' : return '22.7 Simulations and drills are conducted with national authorities and other organisations.'
    elif q == 'a3c7q7' : return 'Component 22 performance'
    elif q == 'a3c8q0' : return '23.1 Key staff are familiar with the available IFRC/ICRC support (technical financial material and HR).'
    elif q == 'a3c8q1' : return '23.2 SOPs and contacts to coordinate response with respective IFRC offices are available.'
    elif q == 'a3c8q2' : return '23.3 NS SOPs include procedures to request and incorporate regional and global support/teams into their response system including prior to imminent crisis/disaster.'
    elif q == 'a3c8q3' : return '23.4 NS informs IFRC within 24 hours for which assistance may be required .'
    elif q == 'a3c8q4' : return '23.5 NS is familiar with the IFRC emergency funding mechanisms (Emergency Appeals DREF and Forecast-based Financing by DREF) their procedures and required supporting documents (EPoA).'
    elif q == 'a3c8q5' : return '23.6 NS request bilateral assistance in accordance with established coordination frameworks.'
    elif q == 'a3c8q6' : return '23.7 NS has an assigned focal point to act as counterpart to regional/international responders.'
    elif q == 'a3c8q7' : return 'Component 23 performance'
    elif q == 'a3-2c1q0' : return '14.1 NS ensures the active participation and reflects community needs and strengths of the local population (including marginalized and excluded groups) in the assessment design planning of community-based preparedness activities.'
    elif q == 'a3-2c1q1' : return '14.2 NS conducts regular awareness raising and public education on disaster/crises.'
    elif q == 'a3-2c1q2' : return '14.3 Community based early warning and early action is in place and linked to the local early warning systems.'
    elif q == 'a3-2c1q3' : return '14.4 CDRTs are trained and equipped to handle local response in partnership with relevant local actors.'
    elif q == 'a3-2c1q4' : return '14.5 CDRTs have an up-to-date response and contingency plan aligned with relevant local plans and resources.'
    elif q == 'a3-2c1q5' : return '14.6 NS ensures community assessment planning and response is done in an inclusive gender and diversity and conflict sensitive way.'
    elif q == 'a3-2c1q6' : return 'Component 14A performance'
    elif q == 'a3-2c2q0' : return '14.7 Evacuation is part of NS\'s response strategy and is identified in different scenarios.'
    elif q == 'a3-2c2q1' : return '14.8 NS is part of the mechanism for the evacuation of communities in high-risk areas.'
    elif q == 'a3-2c2q2' : return 'Component 14B performance'
    elif q == 'a3-2c3q0' : return '14.9 Multi-sectoral response needs are identified for different epidemic scenarios including multi-country outbreaks.'
    elif q == 'a3-2c3q1' : return '14.10 NS has procedures data collection and feedback mechanisms in place to ensure community engagement in prevention and response interventions.'
    elif q == 'a3-2c3q2' : return '14.11 NS has a procedure in place to manage and respond to rumours.'
    elif q == 'a3-2c3q3' : return '14.12 NS has safety protocols in place for paid staff and volunteers for infection prevention and control within epidemics.'
    elif q == 'a3-2c3q4' : return '14.13 NS is part of the public authorities\' safe and dignified management of dead bodies and identification system in infectious disease outbreaks.'
    elif q == 'a3-2c3q5' : return '14.14 NS has appropriate personal protection equipment in place with regularly trained staff and volunteers on handling using and disposing this equipment.'
    elif q == 'a3-2c3q6' : return '14.15 NS has clearly identified their role within epidemics and have established relevant technical support to ensure best practice.'
    elif q == 'a3-2c3q7' : return '14.16 NS has clearly identified their role in the case of isolation and quarantine being declared and have established relevant technical support to ensure best practice.'
    elif q == 'a3-2c3q8' : return 'Component 14C performance'
    elif q == 'a3-2c4q0' : return '14.17 First Aid is part of NS\'s response strategy and is identified in different scenarios.'
    elif q == 'a3-2c4q1' : return '14.18 NS includes First Aid training as part of its CBDRR strategy.'
    elif q == 'a3-2c4q2' : return '14.19 NS has trained and equipped teams of First Aid volunteers for quick and effective response.'
    elif q == 'a3-2c4q3' : return 'Component 14D performance'
    elif q == 'a3-2c5q0' : return '14.20 Water and sanitation humanitarian consequences are part of the NS\'s response strategy and identified in different scenarios.'
    elif q == 'a3-2c5q1' : return '14.21 NS response teams (national and branch) have the appropriate WASH training skills and equipment.'
    elif q == 'a3-2c5q2' : return '14.22 NS has the required equipment to provide quality WASH services or clear SOPs on how to obtain this equipment (in-country or via IFRC).'
    elif q == 'a3-2c5q3' : return '14.23 WASH technical support in emergencies is available in the NS through RCRC Movement partners or agreed with relevant WASH authorities/ partners.'
    elif q == 'a3-2c5q4' : return '14.24 NS is engaged and coordinates with other organizations and networks active in WASH in the country.'
    elif q == 'a3-2c5q5' : return 'Component 14E performance'
    elif q == 'a3-2c6q0' : return '14.25 NS monitors analyses and documents food security levels in the country food-security status of the population/most vulnerable agro-meteorological data supplies and demand in main food and agricultural markets food reserves.'
    elif q == 'a3-2c6q1' : return '14.26 NS has technical staff for food assistance trained to assess needs and make recommendations on assistance needed transfer modality (cash food vouchers) and delivery mechanism according to markets’ conditions.'
    elif q == 'a3-2c6q2' : return '14.27 NS is engaged and coordinated with other organizations and networks (clusters) active in food aid distribution (WFP ICRC…).'
    elif q == 'a3-2c6q3' : return '14.28 NS has integrated food distribution in its response strategies (main risks scenarios response capacity) and adheres to policy and safety standards for food and milk distribution.'
    elif q == 'a3-2c6q4' : return '14.29 NS has a specific action plan to procure and distribute food aid at scale including assessment forms SOPs for Affected population identification and selection food ration calculation (based on food access and availability at the household level) different types of food distribution system set up of distribution site.'
    elif q == 'a3-2c6q5' : return 'Component 14F performance'
    elif q == 'a3-2c7q0' : return '14.30 Livelihoods is incorporated into NS DM/DP strategy plans systems and procedures.'
    elif q == 'a3-2c7q1' : return '14.31 NS has identified national policies related to safety nets employment and livelihood/economic/resilience development plans.'
    elif q == 'a3-2c7q2' : return '14.32 NS has identified a Livelihood household/FS focal point and other technical staff (emergency response teams) for livelihoods preparedness who are trained on assessment market analysis etc.'
    elif q == 'a3-2c7q3' : return '14.33 NS has identified and documented main livelihoods zones and systems (agricultural and non-agricultural) and main market systems (food and household livelihood) in disaster-prone areas which are used to develop and update a market baseline.'
    elif q == 'a3-2c7q4' : return '14.34 NS has identified risks to community and household productive assets in disaster-prone areas and has plans for protection in place.'
    elif q == 'a3-2c7q5' : return '14.35 NS emergency tools are contextualised and include livelihoods.'
    elif q == 'a3-2c7q6' : return '14.36 NS is engaged and coordinated with other organizations and networks active in livelihoods in the country.'
    elif q == 'a3-2c7q7' : return '14.37 NS staff and volunteers are trained in data collection (for baseline and progress/indicators measurement).'
    elif q == 'a3-2c7q8' : return 'Component 14G performance'
    elif q == 'a3-2c8q0' : return '14.38 Search and rescue is part of the NS\'s response strategy and is identified in different scenarios.'
    elif q == 'a3-2c8q1' : return 'Component 14H performance'
    elif q == 'a3-2c9q0' : return '14.39 NS has mechanisms for consultation with target population on the most appropriate shelter response solutions.'
    elif q == 'a3-2c9q1' : return '14.40 Based on the scenario agreed with the public authorities shelter supplies are pre-positioned in high-risk areas.'
    elif q == 'a3-2c9q2' : return '14.41 NS has an agreed standard NFI kit with items prepositioned and clear SOPs on how to obtain them (in-country or via IFRC).'
    elif q == 'a3-2c9q3' : return '14.42 NS has identified suppliers of shelter items and NFIs with pre-disaster and framework agreements in place.'
    elif q == 'a3-2c9q4' : return '14.43 NS has standard emergency and temporary shelter designs following consultation with at risk population and based on available materials and common techniques.'
    elif q == 'a3-2c9q5' : return '14.44 NS volunteers are trained in the use of the prepositioned shelter materials to construct basic shelters (e.g. shelter kit training).'
    elif q == 'a3-2c9q6' : return 'Component 14I performance'
    elif q == 'a3-2c10q0' : return '14.45 NS is part of the public authorities\' management of dead bodies and identification system.'
    elif q == 'a3-2c10q1' : return '14.46 Management of dead bodies and identification needs are part of the NS\'s response strategy and identified in different scenarios.'
    elif q == 'a3-2c10q2' : return 'Component 14J performance'
    elif q == 'a3-2c11q0' : return '14.47 Staff and volunteers are able to provide quality RFL services.'
    elif q == 'a3-2c11q1' : return '14.48 Procedures and agreements with ICRC on RFL are in place.'
    elif q == 'a3-2c11q2' : return 'Component 14K performance'
    elif q == 'a3-2c12q0' : return '14.49 Key staff are familiar with key recovery principles such as detailed assessment community participation consideration of cross-cutting issues and strengthening resilience through the response.'
    elif q == 'a3-2c12q1' : return '14.50 The NS mandate for recovery is formally agreed with the public authorities.'
    elif q == 'a3-2c12q2' : return '14.51 NS has set up enabling systems which smoothen the transition from relief to longer-term recovery activities including human resources and support services as well as planning for early recovery interventions.'
    elif q == 'a3-2c12q3' : return '14.52 NS coordinates with public authorities and humanitarian actors participating in joint needs assessment and the national recovery and reconstruction planning.'
    elif q == 'a3-2c12q4' : return '14.53 NS volunteers are trained in the use of the prepositioned shelter materials to construct basic shelters (e.g. shelter kit training).'
    elif q == 'a3-2c12q5' : return '14.54 NS has considered the possibility of external partnerships to meet recovery needs especially in sectors which are not considered strategic.'
    elif q == 'a3-2c12q6' : return 'Component 14L performance'
    elif q == 'a3-2c13q0' : return '14.55 NS has a defined role and allied responsibilities in national regional and local authorities\' emergency plans related to CBRN hazards.'
    elif q == 'a3-2c13q1' : return '14.56 NS has an action plan to respond to a technological and biological incident based on its agreed role.'
    elif q == 'a3-2c13q2' : return '14.57 NS has SOPs including safety protocols for CBRN related operations.'
    elif q == 'a3-2c13q3' : return '14.58 NS has a dedicated focal point for CBRN.'
    elif q == 'a3-2c13q4' : return '14.59 NS has according to its mandate specifically trained staff and volunteers able to effectively operate in CBRN preparedness and response environments.'
    elif q == 'a3-2c13q5' : return '14.60 NS has appropriate CBRN personal protection equipment in place and regularly trains staff and volunteers on handling and using this equipment.'
    elif q == 'a3-2c13q6' : return '14.61 NS has built up a network of expertise with relevant organizations and key experts to receive specialized support for CBRN-related hazards.'
    elif q == 'a3-2c13q7' : return '14.62 NS in line with its mandate has readily available public key messages for CBRN emergencies that have been vetted by the relevant civil authorities.'
    elif q == 'a3-2c13q8' : return '14.63 NS has engaged with neighboring National Societies in planning for and responding to the cross-border effects of CBRN hazards.'
    elif q == 'a3-2c13q9' : return '14.64 The NS is participating in relevant CBRN-related forums (national/regional) for preparedness and response and has the mechanisms for real-time information sharing.'
    elif q == 'a3-2c13q10' : return '14.65 The NS has identified the need for international assistance for CBRN events (if applicable) and has shared this with Movement partners.'
    elif q == 'a3-2c13q11' : return 'Component 14M performance'
    elif q == 'a3-2c14q0' : return '14.66 Community health volunteers discuss and develop health contingency plans with their communities and conduct community health and safety assessments once a year.'
    elif q == 'a3-2c14q1' : return '14.67 Every volunteer in every sector is initially trained in Basic First Aid and receives refresher training each year.'
    elif q == 'a3-2c14q2' : return '14.68 CBHFA volunteer training includes a session on proper reporting of suspect health events to branch staff and/or the Ministry of Health'
    elif q == 'a3-2c14q3' : return '14.69 CBHFA volunteers are actively engaged in simulation planning implementation and evaluation to ensure community awareness and involvement and that information and referral linkages with health facilities are maintained.'
    elif q == 'a3-2c14q4' : return 'Component 14N performance'
    elif q == 'a4c0q0' : return '24.1 All coordination and cooperation adheres to SMCC principles.'
    elif q == 'a4c0q1' : return '24.2 In country coordination mechanisms are established with Movement partners to share information on needs assessment plan of actions progress against operations and emerging gaps in resources and operational capacities.'
    elif q == 'a4c0q2' : return '24.3 NS exchanges information with neighboring NS and coordinates its response activities with them.'
    elif q == 'a4c0q3' : return '24.4 When international assistance is accepted the NS establishes a framework to receive coordinate account and report on its use in collaboration with IFRC.'
    elif q == 'a4c0q4' : return 'Component 24 performance'
    elif q == 'a4c1q0' : return '25.1 NS is formally part of the national humanitarian coordination system participates regularly and informs partners on RCRC Movement capacities in case international support is required.'
    elif q == 'a4c1q1' : return '25.2 NS knows the national authorities\' capacities and identifies areas within a response to fulfill their auxiliary role.'
    elif q == 'a4c1q2' : return '25.3 NS maintains control over assets resources and use of emblem when working with public authorities and ensures independence.'
    elif q == 'a4c1q3' : return '25.4 Each NS area of intervention has an established coordination mechanism with local and national authorities.'
    elif q == 'a4c1q4' : return 'Component 25 performance'
    elif q == 'a4c2q0' : return '26.1 NS is an active member of the humanitarian community (UN NGO) for coordination and efficiency of response.'
    elif q == 'a4c2q1' : return '26.2 The role of the NS as a cluster member is formally agreed and NS provides information to the humanitarian coordination system.'
    elif q == 'a4c2q2' : return '26.3 NS is aware of IFRC\'s role in the shelter cluster coordination.'
    elif q == 'a4c2q3' : return '26.4 NS is aware of UN-led appeal and strategic processes.'
    elif q == 'a4c2q4' : return '26.5 Partnership agreements with key emergency response UN/NGO partners in country are formalized and shared between branches and headquarters.'
    elif q == 'a4c2q5' : return 'Component 26 performance'
    elif q == 'a4c3q0' : return '27.1 Coordination arrangements exist with military and adhere to Fundamental Principles International humanitarian law (IHL) Council of Delegates (CoD) resolutions.'
    elif q == 'a4c3q1' : return '27.2 NS applies the Movement guidance document on the Movement and military bodies (2005).'
    elif q == 'a4c3q2' : return '27.3 NS only uses military assets as a last resort in coordination with local authorities and informing IFRC.'
    elif q == 'a4c3q3' : return '27.4 NS considers potential impact on security of affected population when coordinating with military forces and does not use armed protection or armed military transport.'
    elif q == 'a4c3q4' : return '27.5 NS promotes Fundamental Principles and appropriate use of the Movement emblems.'
    elif q == 'a4c3q5' : return 'Component 27 performance'
    elif q == 'a4c4q0' : return '28.1 NS has procedures to manage information between community to branches and branch to headquarters and vice versa.'
    elif q == 'a4c4q1' : return '28.2 Information from communities is taken into consideration for decision-making at branches and shared with headquarters.'
    elif q == 'a4c4q2' : return '28.3 Branches have system to communicate and coordinate with CDRTs.'
    elif q == 'a4c4q3' : return '28.4 NS supports community level response systems (either within the NS or in coordination with local authorities).'
    elif q == 'a4c4q4' : return 'Component 28 performance'
    elif q == 'a4c5q0' : return '29.1 NS ensures due diligence when selecting partners and accepting donations to mitigate image or reputational risks.'
    elif q == 'a4c5q1' : return '29.2 NS ensures appropriate use of emblem and protect the organization\'s visual identity.'
    elif q == 'a4c5q2' : return '29.3 NS has mechanisms in place to train and use volunteers from corporate partners.'
    elif q == 'a4c5q3' : return 'Component 29 performance'
    elif q == 'a5c0q0' : return '30.1 NS implements Safer Access and has appropriate security systems in place to protect staff and volunteers.'
    elif q == 'a5c0q1' : return '30.2 Trained staff at headquarter and branch are appointed and accountable for safety and security.'
    elif q == 'a5c0q2' : return '30.3 Context and risk analysis information is provided to responders on an ongoing basis.'
    elif q == 'a5c0q3' : return '30.4 A safety and security policy and a compliance system exist to monitor staff and volunteers.'
    elif q == 'a5c0q4' : return '30.5 Responders have been trained in Safer Access Stay Safe and managers have completed security management training.'
    elif q == 'a5c0q5' : return '30.6 All staff and volunteers know the NS safety and security rules and procedures and follow them.'
    elif q == 'a5c0q6' : return '30.7 NS has communication mechanisms for staff and volunteers to report safety and security risks and incidents.'
    elif q == 'a5c0q7' : return 'Component 30 performance'
    elif q == 'a5c1q0' : return '31.1 NS has a dedicated PMER function for emergency operations with adequate human and financial resources.'
    elif q == 'a5c1q1' : return '31.2 NS refers to and uses lessons from previous operations in response planning (e.g. from evaluation review and operational reports).'
    elif q == 'a5c1q2' : return '31.3 NS has a standardised framework or plan of action for emergency operations which identifies specific results and the indicators to measure them.'
    elif q == 'a5c1q3' : return '31.4 NS operates a M&E system at the field level to collect manage and report on data to branch country and IFRC offices against the set objectives of the operation.'
    elif q == 'a5c1q4' : return '31.5 Operational plans are revised and updated based on intended and unintended outcomes of operations.'
    elif q == 'a5c1q5' : return '31.6 NS allocates resources to conduct evaluations and/or reviews of the operation to identify and integrate key lessons and recommendations.'
    elif q == 'a5c1q6' : return '31.7 NS reports in a timely manner using appropriate reporting templates/formats according to agreements with partners.'
    elif q == 'a5c1q7' : return '31.8 NS effectively leads or cooperates with the IFRC and ICRC on relevant PMER processes especially the compilation and sharing of Movement-wide contributions to the operation.'
    elif q == 'a5c1q8' : return 'Component 31 performance'
    elif q == 'a5c2q0' : return '32.1 NS has an automated accounting and financial system and procedures to account for and report regularly on funds expenditures and any in-kind resources received.'
    elif q == 'a5c2q1' : return '32.2 NS has trained personnel in Finance and Admin emergency support procedures.'
    elif q == 'a5c2q2' : return '32.3 NS has approved adapted Finance and Admin emergency procedures that comply with national laws and IFRC practices to rapidly support operations.'
    elif q == 'a5c2q3' : return '32.4 The activation of Finance and Admin emergency procedures is linked to the EOC SOPs.'
    elif q == 'a5c2q4' : return '32.5 NS has procedures in place to facilitate transparency.'
    elif q == 'a5c2q5' : return '32.6 NS has in place systems and procedures for control and oversight to prevent acts of fraud and/or corruption during an emergency.'
    elif q == 'a5c2q6' : return '32.7 Relevant admin finance staff and operation managers are familiar with existing emergency related MoUs or agreements for compliance.'
    elif q == 'a5c2q7' : return 'Component 32 performance'
    elif q == 'a5c3q0' : return '33.1 All key staff are equipped with functioning mobile phones SIM cards/load cards are readily available and a system to ensure recharging is in place while in the field.'
    elif q == 'a5c3q1' : return '33.2 NS key personnel carry contact lists at all times with critical numbers saved as standard on all mobile phones.'
    elif q == 'a5c3q2' : return '33.3 NS has an up-to-date approved Emergency Notification Protocol / SOPs followed by all staff and volunteers.'
    elif q == 'a5c3q3' : return '33.4 NS has an agreed social media platform (i.e. WhatsApp Viber Line Facebook etc.) for emergency communications and messaging.'
    elif q == 'a5c3q4' : return '33.5 Key headquarter and branch staff in high-risk areas have a functioning radio system (two-way VHF and HF).'
    elif q == 'a5c3q5' : return '33.6 Handheld radios are assigned to key staff and NS vehicles are equipped with radios.'
    elif q == 'a5c3q6' : return '33.7 Frequencies for emergency radio transmission are officially cleared with national authorities.'
    elif q == 'a5c3q7' : return '33.8 All personnel have received radio training and call signs are assigned accordingly.'
    elif q == 'a5c3q8' : return '33.9 NS has up-to-date approved SOPs for mobile and radio communications.'
    elif q == 'a5c3q9' : return '33.10 NS has assigned satellite phones to key staff (according to context needs) and any country restrictions are known and adhered to.'
    elif q == 'a5c3q10' : return '33.11 NS has portable generators to ensure continuity of operations at key HQ and branch locations.'
    elif q == 'a5c3q11' : return '33.12 NS has an internet capable router to provide data connectivity for operational staff and pocket WiFi devices are available for field personnel.'
    elif q == 'a5c3q12' : return '33.13 NS has trained IT support focal points able to support technical issues and equipment (e.g. computers software phones cameras GPS) and provide maintenance.'
    elif q == 'a5c3q13' : return 'Component 33 performance'
    elif q == 'a5c5q0' : return '34.1 NS has a dedicated function/unit to carry out and coordinate all logistics activities i.e. procurement stock management and warehousing transport and fleet.'
    elif q == 'a5c5q1' : return '34.2 All staff involved in logistics have a clearly defined role in their job descriptions and have received training to carry out their tasks.'
    elif q == 'a5c5q2' : return '34.3 Key staff are familiar with IFRC logistics services to support National Society emergency operations.'
    elif q == 'a5c5q3' : return '34.4 NS has analysed optimal supply chain options (e.g. prepositioned relief items pre-existing agreements with suppliers environmental impact) in terms of cost speed and reliability.'
    elif q == 'a5c5q4' : return '34.5 Pre-positioned relief items meet standards and reflect at risk/affected populations needs.'
    elif q == 'a5c5q5' : return '34.6 Pre-positioned relief items are strategically located in the high risk areas.'
    elif q == 'a5c5q6' : return '34.7 NS has volunteers trained in logistics who can act as surge capacity during an emergency response.'
    elif q == 'a5c6q0' : return '34.8 NS is aware of the existence of any status agreement IFRC has signed with the government and the implications of that agreement on any import duty and tax exemptions.'
    elif q == 'a5c6q1' : return '34.9 NS coordinates their stock and equipment with other key stakeholders in country and adheres to Movement standards (Emergency Items Catalogue).'
    elif q == 'a5c6q2' : return '34.10 A documented expedited procedure exists for branches to request additional relief items and/or equipment for early action and immediate response.'
    elif q == 'a5c6q3' : return '34.11 NS has SOPs for accepting (or rejecting) storing disposing and reporting on in-kind donations.'
    elif q == 'a5c6q4' : return '34.12 NS has a procedure on the import of goods (regulations to comply forms to be completed requirement of import licensed agents etc.) including import tax/duties exemptions.'
    elif q == 'a5c7q0' : return '34.13 NS has trained personnel for procurement.'
    elif q == 'a5c7q1' : return '34.14 NS has a documented and approved emergency procurement procedure including authorisation levels standard forms templates and relevant staff are familiar with the procedure.'
    elif q == 'a5c7q2' : return '34.15 NS has an up-to-date database of suppliers (who are in compliance with IFRC Code of Conduct) for key items and services.'
    elif q == 'a5c7q3' : return '34.16 Supplier database includes the option to blacklist suppliers who are in breach of Code of Conduct or are not performing as per agreement.'
    elif q == 'a5c7q4' : return '34.17 NS has up-to-date pre-agreements with suppliers to be able to immediately access supplies and/or services necessary for humanitarian response.'
    elif q == 'a5c8q0' : return '34.18 NS has a fleet manual including road safety and security vehicle management and maintenance insurance and registration and staff are familiar with content.'
    elif q == 'a5c8q1' : return '34.19 NS vehicles are insured and their use is fully documented through the use of logbooks maintenance records fuel checks etc.'
    elif q == 'a5c8q2' : return '34.20 NS has sufficient and appropriate vehicles (i.e. 4x4 or trucks) owned or contracted for disaster response.'
    elif q == 'a5c8q3' : return '34.21 NS vehicles are fitted with seatbelts fire extinguishers and first aid kits and there is a clear and enforced policy on no weapons in vehicles.'
    elif q == 'a5c8q4' : return '34.22 NS only uses licensed mechanics (or workshops) for its vehicle maintenance.'
    elif q == 'a5c8q5' : return '34.23 NS has documented procedures for recording and reporting of accidents and insurance claims.'
    elif q == 'a5c8q6' : return '34.24 NS has mapped in-country resources to rent or borrow vehicles and/or drivers.'
    elif q == 'a5c8q7' : return '34.25 NS drivers are regularly tested and have valid licenses for the types of vehicles they are driving.'
    elif q == 'a5c8q8' : return '34.26 NS drivers are trained in First Aid defensive driving and Safer Access.'
    elif q == 'a5c8q9' : return '34.27 NS has documented procedures to induct and test new drivers.'
    elif q == 'a5c8q10' : return '34.28 NS has emergency procedures to guide the hours for drivers including non-standard hours and compensation.'
    elif q == 'a5c9q0' : return '34.29 NS has an approved warehouse and stock management manual with standard forms and templates.'
    elif q == 'a5c9q1' : return '34.30 Relevant staff and volunteers are trained on the procedures and use of forms.'
    elif q == 'a5c9q2' : return '34.31 NS has a secure dedicated and appropriate space with 24/7 access to receive store and dispatch relief supplies and response equipment sufficient to cover target number of households as per its response plan.'
    elif q == 'a5c9q3' : return '34.32 NS has storage space (owned rented or shared with other organisations) near high-risk communities accessible during disasters.'
    elif q == 'a5c9q4' : return 'Component 34 performance'
    elif q == 'a5c10q0' : return '35.1 Responders are deployed and equipped according to ToRs.'
    elif q == 'a5c10q1' : return '35.2 NS has learning paths for responders to obtain required qualifications and skills according to competencies and role profiles.'
    elif q == 'a5c10q2' : return '35.3 Responders are trained in quality and accountability standards (Sphere Code of Conduct etc...) around the protection sexual abuse exploitation child protection gender-based violence and other forms of abuse.'
    elif q == 'a5c10q3' : return '35.4 Responders have official updated ID recognised by authorities and appropriate visibility items.'
    elif q == 'a5c10q4' : return '35.5 Responders are regularly briefed on safety and security risks and are appropriately insured.'
    elif q == 'a5c10q5' : return '35.6 Procedures exist to activate deploy and manage branch and national response teams.'
    elif q == 'a5c10q6' : return '35.7 NS has an accessible up-to-date database of responders contacts and capacities at branch and HQ level.'
    elif q == 'a5c10q7' : return '35.8 NS incorporates response volunteers from relevant sectors to maintain a diverse workforce.'
    elif q == 'a5c10q8' : return '35.9 NS has expedited procedures to incorporate spontaneous volunteers during emergencies which meet minimum screening procedures and comply with its volunteer in emergency policy.'
    elif q == 'a5c10q9' : return '35.10 NS has HR procedures to scale-up and down (recruitment retention) and procedures for appreciation of volunteers during emergencies.'
    elif q == 'a5c10q10' : return '35.11 NS has a formal personnel rotation and retention strategy for response.'
    elif q == 'a5c10q11' : return '35.12 For scenarios that entail safety and/or security concerns for staff and volunteers a specific Safer Access analysis is conducted.'
    elif q == 'a5c10q12' : return '35.13 Training on self-care violence and harassment in the workplace is completed regularly and psychosocial support is available for staff and volunteers during and after emergencies and crises.'
    elif q == 'a5c10q13' : return '35.14 NS has a policy to cover responders\' expenses incurred during emergencies.'
    elif q == 'a5c10q14' : return '35.15 The Code of Conduct is signed by all NS staff and volunteers.'
    elif q == 'a5c10q15' : return 'Component 35 performance'
    elif q == 'a5c11q0' : return '36.1 Communications focal points are identified and trained at headquarters and branch level.'
    elif q == 'a5c11q1' : return '36.2 An official spokesperson is designated in an emergency.'
    elif q == 'a5c11q2' : return '36.3 NS uses public and social media to draw attention to unmet needs and rights of affected people.'
    elif q == 'a5c11q3' : return '36.4 Standard templates for communication are available.'
    elif q == 'a5c11q4' : return '36.5 External communication plan is available and implemented and NS provides information to public on emergency situation within 24 hours.'
    elif q == 'a5c11q5' : return '36.6 Key messages and public awareness messages in an emergency are developed and shared with staff regularly.'
    elif q == 'a5c11q6' : return '36.7 NS has capacity to track negative media and social media and react accordingly.'
    elif q == 'a5c11q7' : return '36.8 NS coordinates with IFRC/ICRC on joint communication (SMCC).'
    elif q == 'a5c11q8' : return '36.9 NS has a social networking policy and guidelines to ensure appropriate conduct of staff and volunteers.'
    elif q == 'a5c11q9' : return '36.10 NS has capacity to generate evidence-based results/messages to advocate targeted audiences i.e. decision makers and communities.'
    elif q == 'a5c11q10' : return 'Component 36 performance'
    elif q == 'a5c12q0' : return '37.1 Key staff are familiar with resource mobilisation options for humanitarian operations.'
    elif q == 'a5c12q1' : return '37.2 NS mobilises resources for its preparedness activities.'
    elif q == 'a5c12q2' : return '37.3 NS has a resource mobilisation strategy based on the response strategy available funds and the scale of need.'
    elif q == 'a5c12q3' : return '37.4 NS has agreements and mechanisms for collaboration and fundraising with the private sector.'
    elif q == 'a5c12q4' : return '37.5 Branches in highly vulnerable areas have a resource mobilisation plan.'
    elif q == 'a5c12q5' : return '37.6 NS has established a national emergency fund with criteria for proper use.'
    elif q == 'a5c12q6' : return '37.7 A resource mobilisation focal point is involved in emergency operations coordination.'
    elif q == 'a5c12q7' : return '37.8 NS resource mobilisation has established pre-disaster agreements with partners and donors.'
    elif q == 'a5c12q8' : return '37.9 NS has agreed procedures across departments (technical teams and support services) to communicate changes and report on outcomes of resources provided.'
    elif q == 'a5c12q9' : return '37.10 NS has a platform (phone number bank account online etc.) to accept national and/or international donations within 48 hours of an emergency.'
    elif q == 'a5c12q10' : return '37.11 NS has a pre-defined list of acceptable in-kind donations and complies in an emergency to mitigate image or reputational risks.'
    elif q == 'a5c12q11' : return '37.12 NS has a donation tracking system and works with the IFRC on joint operational shared services platforms (Mob table etc.).NS has a donation tracking system and works with the IFRC on joint operational shared services platforms (Mob table etc.).'
    elif q == 'a5c12q12' : return 'Component 37 performance'
    else:
        return ''

class FormData(models.Model):
    """ PER form data """
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    question_id = models.CharField(max_length=10)
    selected_option = EnumIntegerField(Status)
    notes = models.TextField()

    class Meta:
        ordering = ('form', 'question_id')
        verbose_name = 'Form Data'
        verbose_name_plural = 'Form Data'

    def __str__(self):

        #return '%s / %s' % (self.question_id, self.form)
        return question_details(self.question_id, self.form.code)

class PriorityValue(IntEnum):
    LOW  = 0
    MID  = 1
    HIGH = 2

class WorkPlanStatus(IntEnum):
    STANDBY            = 0
    ONGOING            = 1
    CANCELLED          = 2
    DELAYED            = 3
    PENDING            = 4
    NEED_IMPROVEMENTS  = 5
    FINISHED           = 6
    APPROVED           = 7
    CLOSED             = 8

class WorkPlan(models.Model):
    prioritization = EnumIntegerField(PriorityValue)
    components = models.CharField(max_length=900,null=True, blank=True)
    benchmark = models.CharField(max_length=900,null=True, blank=True)
    actions = models.CharField(max_length=900,null=True, blank=True)
    comments = models.CharField(max_length=900,null=True, blank=True)
    timeline = models.DateTimeField()
    status = EnumIntegerField(WorkPlanStatus)
    support_required = models.BooleanField(default=False)
    focal_point = models.CharField(max_length=90,null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=10, null=True, blank=True)
    question_id = models.CharField(max_length=10, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('prioritization', 'country')
        verbose_name = 'PER Work Plan'
        verbose_name_plural = 'PER Work Plans'

    def __str__(self):
        if self.country is None:
            name = None
        else:
            name = self.country.society_name
        if self.question_id and self.code:
            verbose = question_details(self.question_id, self.code)
            if verbose and name:
                return '%s, %s' % (name, verbose)
        return '%s [%s %s]' % (name, self.code, self.question_id)

class CAssessmentType(IntEnum):
    SELF_ASSESSMENT  = 0
    SIMULATION       = 1
    OPERATIONAL      = 2
    POST_OPERATIONAL = 3

class Overview(models.Model):
    # Without related_name Django gives: Reverse query name for 'Overview.country' clashes with field name 'Country.overview'.
    country = models.ForeignKey(Country, related_name='asmt_country', null=True, blank=True, on_delete=models.SET_NULL)
    # national_society = models.CharField(max_length=90,null=True, blank=True) Redundant
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date_of_current_capacity_assessment = models.DateTimeField()
    type_of_capacity_assessment = EnumIntegerField(CAssessmentType, default=CAssessmentType.SELF_ASSESSMENT)
    date_of_last_capacity_assessment = models.DateTimeField(null=True, blank=True)
    type_of_last_capacity_assessment = EnumIntegerField(CAssessmentType, default=CAssessmentType.SELF_ASSESSMENT)
    branch_involved = models.CharField(max_length=90,null=True, blank=True)
    focal_point_name = models.CharField(max_length=90,null=True, blank=True)
    focal_point_email = models.CharField(max_length=90,null=True, blank=True)
    had_previous_assessment = models.BooleanField(default=False)
    focus = models.CharField(max_length=90,null=True, blank=True)
    facilitated_by = models.CharField(max_length=90,null=True, blank=True)
    facilitator_email = models.CharField(max_length=90,null=True, blank=True)
    phone_number = models.CharField(max_length=90,null=True, blank=True)
    skype_address = models.CharField(max_length=90,null=True, blank=True)
    date_of_mid_term_review = models.DateTimeField()
    approximate_date_next_capacity_assmt = models.DateTimeField()

    class Meta:
        ordering = ('country',)
        verbose_name = 'PER General Overview'
        verbose_name_plural = 'PER General Overviews'

    def __str__(self):
        if self.country is None:
            name = None
        else:
            name = self.country.society_name
        return '%s (%s)' % (name, self.focal_point_name)

class Visibilities(IntEnum):
    HIDDEN = 0
    VISIBLE = 1


def nice_document_path(instance, filename):
    return 'perdocs/%s/%s' % (instance.country.id, filename)


class NiceDocument(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    document = models.FileField(null=True, blank=True, upload_to=nice_document_path, storage=AzureStorage())
    document_url = models.URLField(blank=True)
    country = models.ForeignKey(Country, related_name='perdoc_country', null=True, blank=True, on_delete=models.SET_NULL)
    visibility = EnumIntegerField(Visibilities, default=Visibilities.VISIBLE)

    class Meta:
        ordering = ('visibility', 'country')
        verbose_name = 'PER Document'
        verbose_name_plural = 'PER Documents'

    def __str__(self):
        return '%s - %s' % (self.country, self.name)

