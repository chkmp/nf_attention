# Add libraries
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(WRS2)

# Specify your column names (ROIs)
column_names <- c("visfAtlas", "Attention Mask", "MNI Brain Mask", "Grey Matter mask", "Dynamic localizer", "Static localizer")


# Read the CSV files for both designs
data_short_block <- read_csv('/path/to/one/run04/dataset/neg_log_p_values_summary_run-04.csv', col_names = column_names) %>%
  mutate(Design = "Short Block")


data_long_block <- read_csv('/path/to/run06/dataset/neg_log_p_values_summary_run-06.csv', col_names = column_names) %>%
  mutate(Design = "Long Block")


# Add a participant ID to each dataset before combining them.
# This assumes that participant IDs are in the same order in both datasets.
participant_ids <- 1:10 

data_short_block$Participant <- participant_ids
data_long_block$Participant <- participant_ids

# Combine the datasets
data_combined <- bind_rows(data_long_block, data_short_block)

# Convert the data from wide to long format, including the design type
data_long <- pivot_longer(data_combined, -c(Participant, Design), names_to = "ROI", values_to = "Accuracy")

#rearrange so all participants grouped together 
data_long <- data_long %>%
  arrange(Participant, Design)

# Convert 'Participant' to a factor
data_long$Participant <- as.factor(data_long$Participant)

data_long <- data_long %>%
  arrange(Participant, Design)

# Convert tibble to standard data frame
data_long_df <- as.data.frame(data_long)


# Ensuring 'ROI' and 'Design' are factors
data_long_df$ROI <- as.factor(data_long$ROI)
data_long_df$Design <- as.factor(data_long$Design)


####SHORT BLOCK###########

visfAtlas_short <- data_long_df %>%
  filter(Design == "Short Block", ROI == "visfAtlas") %>%
  pull(Accuracy)

attention_short <- data_long_df %>%
  filter(Design == "Short Block", ROI == "Attention Mask") %>%
  pull(Accuracy)

mni_short <- data_long_df %>%
  filter(Design == "Short Block", ROI == "MNI Brain Mask") %>%
  pull(Accuracy)

grey_short <- data_long_df %>%
  filter(Design == "Short Block", ROI == "Grey Matter mask") %>%
  pull(Accuracy)

dynamic_short <- data_long_df %>%
  filter(Design == "Short Block", ROI == "Dynamic localizer") %>%
  pull(Accuracy)

static_short <- data_long_df %>%
  filter(Design == "Short Block", ROI == "Static localizer") %>%
  pull(Accuracy)

########long block#######################

visfAtlas_long <- data_long_df %>%
  filter(Design == "Long Block", ROI == "visfAtlas") %>%
  pull(Accuracy)

attention_long <- data_long_df %>%
  filter(Design == "Long Block", ROI == "Attention Mask") %>%
  pull(Accuracy)

mni_long <- data_long_df %>%
  filter(Design == "Long Block", ROI == "MNI Brain Mask") %>%
  pull(Accuracy)

grey_long <- data_long_df %>%
  filter(Design == "Long Block", ROI == "Grey Matter mask") %>%
  pull(Accuracy)

dynamic_long <- data_long_df %>%
  filter(Design == "Long Block", ROI == "Dynamic localizer") %>%
  pull(Accuracy)

static_long <- data_long_df %>%
  filter(Design =="Long Block", ROI == "Static localizer") %>%
  pull(Accuracy)

# Create a list of all vectors
all_vectors <- list(
  visfAtlas_short = visfAtlas_short,
  attention_short = attention_short,
  mni_short = mni_short,
  grey_short = grey_short,
  dynamic_short = dynamic_short,
  static_short = static_short,
  visfAtlas_long = visfAtlas_long,
  attention_long = attention_long,
  mni_long = mni_long,
  grey_long = grey_long,
  dynamic_long = dynamic_long,
  static_long = static_long
)

# Function to calculate mean, median, and standard deviation, rounded to two decimal places
calculate_stats <- function(vectors_list) {
  stats <- sapply(vectors_list, function(vector) {
    c(mean = round(mean(vector, na.rm = TRUE), 2), 
      median = round(median(vector, na.rm = TRUE), 2), 
      sd = round(sd(vector, na.rm = TRUE), 2))
  }, simplify = FALSE) # Keep as a list
  return(stats)
}

# Apply the function to all vectors
vector_stats <- calculate_stats(all_vectors)

# Print the results
print(vector_stats)

# Perform two-way ANOVA with trimmed means using your data
trimmed_anova_result <- t2way(Accuracy ~ ROI * Design, data = data_long_df)

# Look at the results
trimmed_anova_result



# Filter for short block design and combine all accuracy values into a vector
short_design_vector <- data_long_df %>% 
  filter(Design == "Short Block") %>%
  pull(Accuracy)


#####Vectors for multiple comparisons of Main effects in Anova ################
# Filter for long block design and combine all accuracy values into a vector
long_design_vector <- data_long_df %>% 
  filter(Design == "Long Block") %>%
  pull(Accuracy)

# Filter for short block design and combine all accuracy values into a vector
short_design_vector <- data_long_df %>% 
  filter(Design == "Short Block") %>%
  pull(Accuracy)

# Filter for long block design and combine all accuracy values into a vector
visfAtlas_vector <- data_long_df %>% 
  filter(ROI == "visfAtlas") %>%
  pull(Accuracy)

# Filter for short block design and combine all accuracy values into a vector
attention_mask_vector <- data_long_df %>% 
  filter(ROI == "Attention Mask") %>%
  pull(Accuracy)

# Filter for short block design and combine all accuracy values into a vector
static_localizer_vector <- data_long_df %>% 
  filter(ROI == "Static localizer") %>%
  pull(Accuracy)

# Filter for short block design and combine all accuracy values into a vector
dynamic_localizer_vector <- data_long_df %>% 
  filter(ROI == "Dynamic localizer") %>%
  pull(Accuracy)

# Filter for short block design and combine all accuracy values into a vector
mni_brain_mask_vector <- data_long_df %>% 
  filter(ROI == "MNI Brain Mask") %>%
  pull(Accuracy)

# Filter for short block design and combine all accuracy values into a vector
grey_matter_mask_vector <- data_long_df %>% 
  filter(ROI == "Grey Matter mask") %>%
  pull(Accuracy)

# Define a function for the robust paired t-test
run_yuend_test <- function(vector1, vector2, trim_level = 0.2) {
  yuend(x = vector1, y = vector2, tr = trim_level)
}

# Create a list to hold the results
results_list <- list()

# Run the pairwise comparisons
results_list[["visfAtlas vs. Attention Mask"]] <- run_yuend_test(visfAtlas_vector, attention_mask_vector)
results_list[["visfAtlas vs. MNI Brain Mask"]] <- run_yuend_test(visfAtlas_vector, mni_brain_mask_vector)
results_list[["visfAtlas vs. Grey Matter Mask"]] <- run_yuend_test(visfAtlas_vector, grey_matter_mask_vector)
results_list[["visfAtlas vs. Dynamic localizer"]] <- run_yuend_test(visfAtlas_vector, dynamic_localizer_vector)
results_list[["visfAtlas vs. Static localizer"]] <- run_yuend_test(visfAtlas_vector, static_localizer_vector)
results_list[["Attention Mask vs. MNI Brain Mask"]] <- run_yuend_test(attention_mask_vector, mni_brain_mask_vector)
results_list[["Attention Mask vs. Grey Matter Mask"]] <- run_yuend_test(attention_mask_vector, grey_matter_mask_vector)
results_list[["Attention Mask vs. Dynamic localizer"]] <- run_yuend_test(attention_mask_vector, dynamic_localizer_vector)
results_list[["Attention Mask vs. Static localizer"]] <- run_yuend_test(attention_mask_vector, static_localizer_vector)
results_list[["MNI Brain Mask vs. Grey Matter Mask"]] <- run_yuend_test(mni_brain_mask_vector, grey_matter_mask_vector)
results_list[["MNI Brain Mask vs. Dynamic localizer"]] <- run_yuend_test(mni_brain_mask_vector, dynamic_localizer_vector)
results_list[["MNI Brain Mask vs. Static localizer"]] <- run_yuend_test(mni_brain_mask_vector, static_localizer_vector)
results_list[["Grey Matter Mask vs. Dynamic localizer"]] <- run_yuend_test(grey_matter_mask_vector, dynamic_localizer_vector)
results_list[["Grey Matter Mask vs. Static localizer"]] <- run_yuend_test(grey_matter_mask_vector, static_localizer_vector)
results_list[["Dynamic localizer vs. Static localizer"]] <- run_yuend_test(dynamic_localizer_vector, static_localizer_vector)
results_list[["Short Design vs. Long Design"]] <- run_yuend_test(short_design_vector,long_design_vector)


#for interaction
# Run the pairwise comparisons
results_list[["visfAtlas Short vs.visfAtlas Long" ]] <- run_yuend_test(visfAtlas_short, visfAtlas_long)
results_list[["Attention Mask Short vs. Attention Mask Long"]] <- run_yuend_test(attention_short, attention_long)
results_list[["MNI Brain Mask Short vs. MNI Brain Mask Long"]] <- run_yuend_test(mni_short, mni_long)
results_list[["Grey Matter Mask Short vs. Grey Matter Mask Long"]] <- run_yuend_test(grey_short, grey_long)
results_list[["Dynamic localizer Short vs. Dynamic localizer Long"]] <- run_yuend_test(dynamic_short, dynamic_long)
results_list[["Static localizer Short vs. Static localizer Long"]] <- run_yuend_test(static_short, static_long)


# Print the results
results_list


#for main effect of long/block design
mean_short <-mean(short_design_vector)
mean_long <-mean(long_design_vector)
mean_difference <- mean_short - mean_long
print(mean_difference)

