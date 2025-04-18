library(shiny)
require(ggplot2)
library(plyr)
library(reshape2)

shinyUI(pageWithSidebar(
  headerPanel("Creating and Evaluating Sampling Plans"),
  
  sidebarPanel(
    radioButtons("eord", label = "Distribution Type", list("Binomial/Continuous Lot"="binom","Hypergeometric/Isolated Lot"="hyp")),
    br(),
    conditionalPanel(condition="input.eord=='binom'",
                     
        radioButtons("aord", label = "Create or Evaluate", list("Calculate Sample Size"="create","Evaluate Sampling Plan"="eval")),
        br(),
        conditionalPanel(condition="input.aord=='create'",
                     
              h3('Input the Probability of nonConformance'),
              helpText('NOTE: This can be gathered from the drawing/specification. It will be 1 - Minimum Probability of Conformance (MPC)'),
              numericInput("maxp", "Probability of nonConformance:", 0.2),
                     
              h3('Input the Consumer Risk (alpha)'),
              helpText('NOTE: This can be gathered from the drawing/specification'),
              helpText('NOTE: A "Rejectable Quality Level, or RQL" based sampling plan has a consumer risk of 0.05'),
              helpText('NOTE: A "Lot Tolerance Percent Defective, or LTPD" based sampling plan has a consumer risk of 0.1'),
              numericInput("alp", "Consumer Risk:", 0.05)
              ),
                     
        conditionalPanel(condition="input.aord=='eval'",
                                      
              h3('Input the Probability of nonConformance'),
              numericInput("maxp", "Probability of nonConformance:", 0.2, min = 0, max = 1, step = 0.01),
                                      
              h3('Input the Lot Size'),
              numericInput("N", "Lot Size:", 500),
                                      
              h3('Input the Sample Size'),
              numericInput("n", "Sample Size:", 30)
              )),
                        
    conditionalPanel(condition="input.eord=='hyp'",
                                         
        radioButtons("aord", label = "Create or Evaluate", list("Calculate Sample Size"="create","Evaluate Sampling Plan"="eval")),
        br(),
        conditionalPanel(condition="input.aord=='create'",
                                                          
              h3('Input the Lot Size'),
              numericInput("N", "Lot Size:", 50),
                                                          
              h3('Input the average Defect Count per lot'),
              numericInput("D", "Defect Count:", 5),
                                                          
              h3('Input the Consumer Risk (alpha)'),
              helpText('NOTE: This can be gathered from drawings/specifications'),
              helpText('NOTE: A "Rejectable Quality Level, or RQL" based sampling plan has a consumer risk of 0.05'),
              helpText('NOTE: A "Lot Tolerance Percent Defective, or LTPD" based sampling plan has a consumer risk of 0.1'),
              numericInput("alp", "Consumer Risk:", 0.1, min = 0, max = 1, step = 0.01)
              ),
                                                          
                            conditionalPanel(condition="input.aord=='eval'",
                                      h3('Input the average Number of Defects per Lot'),
                                      numericInput("D", "Defect Count:", 4),
                                                                           
                                      h3('Input the Lot Size'),
                                      numericInput("N", "Lot Size:", 50),
                                                                           
                                      h3('Input the Sample Size'),
                                      numericInput("n", "Sample Size:", 10)
                                      
                                      )),
    actionButton("goButton","Submit")


    
  ),
               
    mainPanel(
      
      tabsetPanel(
        
        tabPanel("Introduction",
                 h4('This application is designed to be a guide for designing and evaluating C = 0, attribute data sampling plans.'),
                 tags$img(src = "https://smartersolutions.com/images/operating-characteristic-curve.jpg", width = "600px", height = "400px")
        ),
        
        tabPanel("Continuous Lots Parameters",
          h4('Average Outgoing Quality Limit'),
          verbatimTextOutput("AOQL"),
          h4('Equal Risk Point (consumer risk = producer risk)'),
          verbatimTextOutput("ERP"),
          h4('Lot Tolerance (consumer risk = 0.1)'),
          verbatimTextOutput("LTol"),
          h4('Rejectable Quality Level (consumer risk = 0.05)'),
          verbatimTextOutput("RQL"),
          h4('Sample Size'),
          verbatimTextOutput("findn"),
          #googootags$iframe(src="d6_4800_flowchart.pdf", width="900", height="600")
        ),
        
        tabPanel("Isolated Lot Parameters",
          h4('Average Outgoing Quality Limit'),
          verbatimTextOutput("AOQL.hyp"),
          h4('Equal Risk Point (consumer risk = producer risk)'),
          verbatimTextOutput("ERP.hyp"),
          h4('Lot Tolerance (consumer risk = 0.1)'),
          verbatimTextOutput("LTol.hyp"),
          h4('Rejectable Quality Level (consumer risk = 0.05)'),
          verbatimTextOutput("RQL.hyp"),
          h4('Sample Size'),
          verbatimTextOutput("n.hyp"),
        ),
               
        tabPanel("Continuous Lots Plots",
          plotOutput("all3", width="900", height="600"),
          br(),
          plotOutput("OC", width="900", height="600")
        ),
               
        tabPanel("Isolated Lot Plots",
          plotOutput("all3.hyp", width="900", height="600")
        ),
        
        tabPanel("Definitions",
          h4('Binomial/continuous lot'),
          verbatimTextOutput("binomial"),
          h4('Hypergeometric/isolated lot'),
          verbatimTextOutput("hypergeometric"),
          h4('Lot Size'),
          verbatimTextOutput("lot"),
          h4('Sample Size'),
          verbatimTextOutput("sample"),
          h4('Defect Count'),
          verbatimTextOutput("defects"),
          h4('Probability of nonConformance'),
          verbatimTextOutput("mpc"),
          h4('Consumer Risk'),
          verbatimTextOutput("consumer"),
          h4('Producer Risk'),
          verbatimTextOutput("producer"),
          h4('Average Outgoing Quality Limit'),
          verbatimTextOutput("aoql"),
          h4('Equal Risk Point'),
          verbatimTextOutput("erp"),
          h4('Lot Tolerance'),
          verbatimTextOutput("ltol"),
          h4('Rejectable Quality Level'),
          verbatimTextOutput("rql"),
          h4('Average Outgoing Quality'),
          verbatimTextOutput("aoq")
        ),
      )
    )
  )
)