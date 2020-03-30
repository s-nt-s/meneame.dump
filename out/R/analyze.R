library(rjson)
library(dplyr)
library(ggplot2)

if(!exists("tags")) {
    opeds <- fromJSON(file = "../published.json")

    # Create a data.frame with the relevant information
    Sys.setlocale("LC_TIME", "es_ES.UTF-8")
    tags <- lapply(opeds, function(x) {
                date <- x$date
                date <- as.Date(date, "%Y-%m-%d %H:%M:%S")
                dd <- data.frame(date = as.character(date),
                                 tags = x$tags,
                                 id = x$id)
                return(dd)
    })

    tags <- do.call(rbind, tags)

    # Year column
    tags$year <- strftime(tags$date, "%Y")
}

tags$tags <- as.character(tags$tags)
tags$id <- as.character(tags$id)

# Get number of editorials published per year
n_year <- tags %>% group_by(year) %>% summarise(n_year = length(unique(id)))
tags <- left_join(tags, n_year)

def <- expand.grid(tags = unique(tags$tags), year = unique(tags$year),
                   stringsAsFactors = FALSE)
def$def <- 0

# Count
counts <- tags %>%
    group_by(year, tags) %>%
    summarise(count = n())

counts <- left_join(counts, n_year)
counts$count_n <- counts$count / counts$n_year * 100

# Add default 0
counts <- left_join(def, counts)
counts[is.na(counts)] <- 0

plt1 <- ggplot(filter(counts, tags %in% c("Corrupción", "Chavismo", "Venezuela", "Podemos", "ETA"))) +
        geom_line(aes(x = year, y = count_n, color = tags, group = tags)) +
        theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
        ggtitle("Porcentaje de portadas dedicadas por Meneame,\n por año, a...") +
        xlab("Año") + ylab("Porcentaje")
print(plt1)
