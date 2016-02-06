SCDB_ISSUES_FILE = 'data/scdb/SCDB_2015_01_caseCentered_LegalProvision.csv'
SCDB_CASES_FILE =  'data/scdb/SCDB_2015_01_caseCentered_Citation.csv'
SCDB_VOTES_FILE = 'data/scdb/SCDB_2015_01_justiceCentered_Citation.csv'
SCDB_TEST_FILE = 'data/scdb/SCDB_TEST.csv'
SCDB_HEADERS = ["caseId","docketId","caseIssuesId","voteId","dateDecision","decisionType","usCite","sctCite","ledCite","lexisCite","term","naturalCourt","chief","docket","caseName","dateArgument","dateRearg","petitioner","petitionerState","respondent","respondentState","jurisdiction","adminAction","adminActionState","threeJudgeFdc","caseOrigin","caseOriginState","caseSource","caseSourceState","lcDisagreement","certReason","lcDisposition","lcDispositionDirection","declarationUncon","caseDisposition","caseDispositionUnusual","partyWinning","precedentAlteration","voteUnclear","issue","issueArea","decisionDirection","decisionDirectionDissent","authorityDecision1","authorityDecision2","lawType","lawSupp","lawMinor","majOpinWriter","majOpinAssigner","splitVote","majVotes","minVotes","justice","justiceName","vote","opinion","direction","majority","firstAgreement","secondAgreement"]
  
DEFAULT_DB = 'sqlite:///scotus.db'
TEST_DB = 'sqlite:///test_scotus.db'