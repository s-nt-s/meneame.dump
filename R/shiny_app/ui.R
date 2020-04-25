#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(ggvis)
library(dplyr)

# Define UI for application that draws a histogram
shinyUI(fluidPage(

  # Application title
  titlePanel("Meneame - fracción de portadas por año y tema"),
  mainPanel(
      uiOutput("ggvis_ui"),
      ggvisOutput("ggvis")
  )
))
