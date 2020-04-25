#
# This is the server logic of a Shiny web application. You can run the
# application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(ggvis)
library(dplyr)

# Define server logic required to draw a histogram
shinyServer(function(input, output) {

    load("counts.Rda")

    s_tags <- counts %>% group_by(tags) %>% summarise(n = sum(count)) %>% arrange(desc(n))
    s_tags <- s_tags$tags

    counts$year <- as.numeric(counts$year)

    counts %>%  ggvis() %>%
        filter(tags %in% eval(input_select(s_tags, multiple = TRUE, label = "Temas",
                                           selectize = TRUE,
                                           selected = c("España", "Europa")))) %>%
        group_by(tags) %>%
        layer_paths(~year, ~count_n, stroke = ~tags, strokeWidth := 4) %>%
        add_axis("x", title = "Año") %>%
        add_axis("y", title = "Fracción de portadas [%]") %>%
        add_legend("stroke", title = "Temas") %>%
        bind_shiny("ggvis", "ggvis_ui")

})
