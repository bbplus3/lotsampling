library(shiny)
library(ggplot2)
library(reshape2)
library(plyr)

shinyServer(function(input, output){
  
  #functions
  plotERP <-
    function(n, N, alp = 0.05, print = T) 
    {
      sam_params <- lotsameval(n, N)
      erp <- sam_params$ERP
      Data <- data.frame(sam_params$PA, sam_params$Probs, sam_params$AOQ, sam_params$AFI)
      
      OC <- ggplot(data = Data, aes_string(y = "sam_params.PA", x = "sam_params.Probs")) +
        geom_point() +  
        geom_vline(xintercept = erp, color = "red") +
        theme_bw() 
      return(OC)
    }
  
  plot3 <-
    function(n, N, alp = 0.05, print = TRUE) {
      sam_params <- lotsameval(n, N)
      
      Data3 <- data.frame(sam_params$PA, sam_params$AOQ, sam_params$AFI)
      melt3 <- melt(Data3)
      names(melt3) <- c("SamplingParameter", "Value")
      data3 <- data.frame(melt3$SamplingParameter, melt3$Value, sam_params$Probs)
      names(data3) <- c("SamplingParameter", "Value", "Probability")
      
      all3 <- ggplot(data = data3) +
        geom_line(data = data3, aes_string(x = "Probability", y = "Value", color = "SamplingParameter")) +
        facet_wrap(~SamplingParameter, scales = "free_y", nrow = 3)
      theme_bw() 
      return(all3)
    }
  
  lotsameval <-
    function(n, N, maxp = 0.2) { 
      Probs <- (maxp/200)*0:200
      PA <- pbinom(0, n, Probs)
      AFI <- 1 - (1 - n/N)*PA
      AOQ <- Probs*(1 - AFI)
      AOQL <- ((1 - n/N)/(1 + n))*(n/(n + 1))^n
      ERP <- 1 - (0.5)^(1/n)
      LTol <- 1 - (0.1)^(1/n)
      RQL <- 1 - (0.05)^(1/n)
      list(Sampars = c(n, N, maxp), Probs = Probs, PA = PA, AFI = AFI, AOQ = AOQ, AOQL = AOQL, ERP = ERP, LTol = LTol, RQL = RQL) }
  
  findn <-
    function(maxp, alp) {
      n <- (log(alp))/(log(1 - maxp))
      return(ceiling(n))
    }
  
  smallsameval <-
    function(n, N) {
      D <- 0:N
      PA.hyp <- phyper(0, D, N - D, n)
      AFI.hyp <- 1 - (1 - n/N)*PA.hyp
      AOQ.hyp <- D*(1 - AFI.hyp)/N
      AOQL.hyp <- max(AOQ.hyp)
      ERP.hyp <- min(D[PA.hyp <= 0.5])/N
      LTol.hyp <- min(D[PA.hyp <= 0.1])/N
      RQL.hyp <- min(D[PA.hyp <= 0.05])/N
      list(Probs.hyp=D/N, PA.hyp = PA.hyp, AFI.hyp = AFI.hyp, AOQ.hyp = AOQ.hyp, AOQL.hyp = AOQL.hyp, LTol.hyp = LTol.hyp, RQL.hyp = RQL.hyp, ERP.hyp = ERP.hyp) 
    }
  
  ERPhyp <- 
    function(n, N) {
      D <- 0:N
      PAhyp <- phyper(0, D, N - D, n)
      return(min(D[PAhyp <= 0.5])/N)
    }
  
  LTolhyp <- 
    function(n, N) {
      D <- 0:N
      PAhyp <- phyper(0, D, N - D, n)
      return(min(D[PAhyp <= 0.1])/N)
    }
  
  RQLhyp <- 
    function(n, N) {
      D <- 0:N
      PAhyp <- phyper(0, D, N - D, n)
      return(min(D[PAhyp <= 0.05])/N)
    }
  
  findn.hyp <-
    function(N, D, alp) { 
      maxp <- D/N
      n <- ceiling((log(alp))/(log(1 - maxp)))
      PA <- phyper(0, D, N - D, n)
      while (PA <= alp) {
        n <- n - 1
        PA <- phyper(0, D, N - D, n) 
      }
      n <- n + 1
      return(n)
    }
  
  plot3.hyp <-
    function(n, N) {
      
      small_params <- smallsameval(n, N)
      
      smallData3 <- data.frame(small_params$PA.hyp, small_params$AOQ.hyp, small_params$AFI.hyp)
      smallmelt3 <- melt(smallData3)
      names(smallmelt3) <- c("SamplingParameter", "Value")
      smalldata3 <- data.frame(smallmelt3$SamplingParameter, smallmelt3$Value, small_params$Probs)
      names(smalldata3) <- c("SamplingParameter", "Value", "Probability")
      
      all3.hyp <- ggplot(data = smalldata3) +
        geom_line(data = smalldata3, aes_string(x = "Probability", y = "Value", color = "SamplingParameter")) +
        facet_wrap(~SamplingParameter, scales = "free_y", nrow = 3)
      theme_bw() 
      return(all3.hyp)
    }
  
  sample = observe({
    if(input$goButton==0){
      return()
    } else{
      isolate({

        
        if(input$eord=="binom"){
          if(input$aord=="cons"){
          maxp = input$maxp
          alp = input$alp
        } else if(input$aord=="eval"){
          maxp = input$maxp
          n = input$n
          N = input$N
        }} else if(input$eord=="hyp"){
          if(input$aord=="cons"){
         N = input$N
         D = input$D
         alp = input$alp
          } else if(input$aord=="eval"){
            N = input$N
            n = input$n
          }}

  })
  
}})

#     output$findn <- renderText({
#       input$goButton
#       input$alp <- as.numeric(input$alp)
#       input$maxp <- as.numeric(input$maxp)
#       return(ceiling((log(input$alp))/(log(1 - input$maxp))))
#     })

    output$findn <- renderText({
      findn(input$maxp, input$alp)
    })
  
    output$AOQL <- renderPrint({
      ((1 - input$n/input$N)/(1 + input$n))*(input$n/(input$n + 1))^input$n    
    })
    
    output$ERP <- renderPrint({
      1 - (0.5)^(1/input$n)    
    })
    
    output$LTol <- renderPrint({
      1 - (0.1)^(1/input$n)    
    })
    
    output$RQL <- renderPrint({
      1 - (0.05)^(1/input$n)    
    })

    output$all3 <- renderPlot({
      plot3(input$n, input$N)
    })

    output$OC <- renderPlot({  
      plotERP(input$n, input$N, alp = 0.05, print = T)
    })

#     output$flowchart <- renderPlot({
#       
#     })

##########################
#hypergeometric output


    output$all3.hyp <- renderPlot({
      plot3.hyp(input$n, input$N)
    })

    output$n.hyp <- renderText({
      findn.hyp(input$N, input$D, input$alp)
    })

    output$AOQL.hyp <- renderPrint({
      max(input$D*(1 - (1 - (1 - input$n/input$N)*(phyper(0, input$D, input$N - input$D, input$n))/input$N)))    
    })

    output$ERP.hyp <- renderPrint({
      ERPhyp(input$n, input$N)
    })

    output$LTol.hyp <- renderPrint({
      LTolhyp(input$n, input$N)    
    })

    output$RQL.hyp <- renderPrint({
      RQLhyp(input$n, input$N)    
    })

##########################
#definition output

output$binomial <- renderText({
  "The discrete probability distribution of the number of successes in a sequence 
  of n independent yes/no experiments, each of which yields success with 
  probability p."
})

output$hypergeometric <- renderText({
  "A discrete probability distribution that describes the probability of k successes 
  in n draws without replacement from a finite population of size N containing exactly 
  K successes. This is in contrast to the binomial distribution, which describes the 
  probability of k successes in n draws with replacement."
})

output$lot <- renderText({
  "A grouping of product, material, or service"
})

output$sample <- renderText({
  "One or more sampling units taken from a population and intended to provide 
information on the population."
})

output$defects <- renderText({
    "Average number of defects in each lot/unit of product."
})

output$mpc <- renderText({
  "The minimum probability of product conformance which the inspection procedure allows."
})

output$consumer <- renderText({
 "The risk of accepting a bad quality lot." 
})

output$producer <- renderText({
  "The risk of rejecting a good quality lot."
})

output$aoql <- renderText({
  "Maximum AOQ over all possible values of 
incoming product quality level for a given acceptance sampling plan."
})

output$erp <- renderText({
  "The fraction defective that results in a 50 percent chance of rejecting the lot. In ANSI/ASQC Z1.4, the ERP is called p.50. At this fraction 
defective, the producer's risk and the consumer's risk are the same, namely 50 percent. 
The Equal Risk Point treats losses associated with these two risks as equally important."
})

output$ltol <- renderText({
  "The quality level at which there is a small chance (usually 10 percent) that a lot will be accepted when sampling inspection is 
employed. A lot with a percent defective above the LTPD will have less chance of being 
accepted. This parameter is also called an LQ, UQL or LQP. Boeing specifically defines 
the Rejectable Quality Level (RQL) to be percent defective at which there is a 5 percent 
probability of acceptance of a given lot"
})

output$rql <- renderText({
  "The minimum percent defective at which a lot will 
have 5 percent or less chance of being accepted when using a sampling plan, or another 
statistically based monitoring system."
})

output$aoq <- renderText({
  "The average quality of outgoing product after 
sampling inspection for a given steady value of incoming product quality."
})

output$occurve <- renderText({
  "The curve of a lot sampling plan which shows 
the percentage of lots which may be accepted under the specified sampling plan for any 
given process quality."
})

output$random <- renderText({
  "A sample of n items taken from a population of N items in such a way 
that all possible combinations of n items have the same probability of being selected. If 
random samples are required, then the method for selecting them shall be verifiable (for 
example, using random numbers, but not reach and grab)."
})
})
