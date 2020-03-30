library(ggvis)
library(dplyr)

load("counts.Rda")

s_tags <- counts %>% group_by(tags) %>% summarise(n = sum(count)) %>% arrange(desc(n))
s_tags <- s_tags$tags

counts$year <- as.numeric(counts$year)

ggvis1 <- counts %>%  ggvis() %>% 
    filter(tags %in% eval(input_select(s_tags, multiple = TRUE, label = "Temas",
                                       selectize = TRUE,
                                       selected = c("España", "Europa")))) %>%
    group_by(tags) %>%
    layer_paths(~year, ~count_n, stroke = ~tags, strokeWidth := 4)
