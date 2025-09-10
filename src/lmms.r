# -------------------------------------------------
# Libraries
# -------------------------------------------------
library(dplyr)
library(readr)
library(car)
library(emmeans)
library(ggplot2)
library(tidyr)
library(glmmTMB)
library(stringr)

# -------------------------------------------------
# Output directory
# -------------------------------------------------
output_dir <- "/path/to/paper_results"

# -------------------------------------------------
# Column names for ROIs
# -------------------------------------------------
column_names <- c(
  "visfAtlas", "Attention Mask", "MNI Brain Mask", 
  "Grey Matter Mask", "Dynamic localizer", "Static localizer", 
  "Ventricle Mask", "SubjectID"
)

# -------------------------------------------------
# Read CSV files (short and long design) and add Design column
# -------------------------------------------------
data_short_block <- read_csv(
  "/path/to/original_accuracies_summary_run-03.csv", col_names = TRUE
) %>%
  rename_with(~ column_names) %>%
  mutate(Design = "Short")

data_long_block <- read_csv(
  "/path/to/original_accuracies_summary_run-05.csv", col_names = TRUE
) %>%
  rename_with(~ column_names) %>%
  mutate(Design = "Long")

data_combined <- bind_rows(data_short_block, data_long_block)

# -------------------------------------------------
# Convert from wide to long format
# -------------------------------------------------
data_long <- pivot_longer(
  data_combined, -c(SubjectID, Design), names_to = "ROI", values_to = "Accuracy"
)

svm_data <- data_long %>%
  mutate(
    ROI = factor(
      ROI, 
      levels = c("visfAtlas", "Attention Mask", "MNI Brain Mask", 
                 "Grey Matter Mask", "Dynamic localizer", "Static localizer", 
                 "Ventricle Mask"),
      ordered = FALSE
    ),
    Design = factor(Design, levels = c("Long", "Short"), ordered = FALSE),
    SubjectID = factor(SubjectID)
  )

# -------------------------------------------------
# Transform accuracy values
# -------------------------------------------------
N <- nrow(svm_data)
measure_data <- svm_data %>%
  mutate(Accuracy = (Accuracy * (N - 1) + 0.5) / N) %>%
  filter(ROI != "Ventricle Mask") %>%
  mutate(
    ROI = factor(
      ROI, 
      levels = c("visfAtlas", "Attention Mask", "MNI Brain Mask", 
                 "Grey Matter Mask", "Dynamic localizer", "Static localizer"),
      ordered = FALSE
    ),
    Design = factor(Design, levels = c("Short", "Long"), ordered = FALSE),
    SubjectID = factor(SubjectID)
  )

# Contrast settings
options(contrasts = c("contr.sum", "contr.poly"))
options("contrasts") 
contrasts(measure_data$Design)
contrasts(measure_data$ROI)

levels(measure_data$ROI)
levels(measure_data$Design)

# -------------------------------------------------
# Fit beta regression model
# -------------------------------------------------
lmm_model <- glmmTMB(
  Accuracy ~ Design * ROI + (1 | SubjectID),
  family = beta_family(link = "logit"),
  data = measure_data
)

summary(lmm_model)

# ANOVA (Type III)
anova_lmm <- car::Anova(lmm_model, type = "III")
print(anova_lmm)

# -------------------------------------------------
# Extract and format fixed effects
# -------------------------------------------------
conf_int <- confint(lmm_model, method = "Wald", level = 0.95)

fixed_effects <- as.data.frame(summary(lmm_model)$coefficients$cond) %>%
  mutate(
    Term = rownames(.),
    Estimate = round(Estimate, 2),
    `Std. Error` = round(`Std. Error`, 2),
    z_value = round(`z value`, 2),
    CI_Lower = round(conf_int[rownames(conf_int) %in% rownames(.), 1], 2),
    CI_Upper = round(conf_int[rownames(conf_int) %in% rownames(.), 2], 2),
    `p-Value` = case_when(
      `Pr(>|z|)` < 0.001 ~ "< .001",
      TRUE ~ gsub("^0", "", formatC(`Pr(>|z|)`, format = "f", digits = 3))
    )
  ) %>%
  select(Term, Estimate, CI_Lower, CI_Upper, z_value, `p-Value`)

# Save ANOVA results
formatted_anova <- as.data.frame(anova_lmm) %>%
  tibble::rownames_to_column("Effect") %>%
  mutate( 
    ChiSq = round(`Chisq`, 2),
    `p-Value` = case_when(
      `Pr(>Chisq)` < 0.001 ~ "< .001",
      TRUE ~ sub("^0", "", as.character(round(as.numeric(`Pr(>Chisq)`), 3)))
    )
  ) %>%
  select(Effect, ChiSq, DF = `Df`, `p-Value`)

write.csv(formatted_anova, file.path(output_dir, "training_anova_results.csv"), row.names = FALSE)
write.csv(fixed_effects, file.path(output_dir, "training_fixed_effects_results.csv"), row.names = FALSE)

# -------------------------------------------------
# ROI pairwise comparisons (Wald, FDR corrected)
# -------------------------------------------------
roi_comparisons <- emmeans(lmm_model, pairwise ~ ROI, adjust = "none")
roi_comparisons_table <- as.data.frame(summary(roi_comparisons$contrasts, infer = c(TRUE, TRUE)))
roi_comparisons_table$FDR_p_value <- p.adjust(roi_comparisons_table$p.value, method = "fdr")

roi_comparisons_table <- roi_comparisons_table %>%
  transmute(
    Contrast = contrast,
    Estimate = round(estimate, 2),
    CI_Lower = round(asymp.LCL, 2),
    CI_Upper = round(asymp.UCL, 2),
    `z-value` = round(z.ratio, 2),
    `p-value` = case_when(
      p.value < 0.001 ~ "<.001",
      TRUE ~ sprintf("%.3f", p.value)
    ),
    `FDR p-value` = case_when(
      FDR_p_value < 0.001 ~ "<.001",
      TRUE ~ sprintf("%.3f", FDR_p_value)
    ),
    `p-value (FDR)` = paste0(`p-value`, " (", `FDR p-value`, ")")
  ) %>%
  select(Contrast, Estimate, CI_Lower, CI_Upper, `z-value`, `p-value (FDR)`)

print(roi_comparisons_table)
write.csv(roi_comparisons_table, file.path(output_dir, "training_roi_pairwise_comparisons_Wald_FDR.csv"), row.names = FALSE)

# -------------------------------------------------
# Plot accuracies
# -------------------------------------------------
design_labels <- c("Long"= "Long", "Short" = "Short")

mask_labels <- c(
  "visfAtlas" = "visfAtlas",
  "Attention Mask" = "Attention Mask",
  "MNI Brain Mask" = "MNI Brain Mask",
  "Grey Matter Mask" = "Grey Matter Mask",
  "Dynamic localizer" = "Dynamic localizer",
  "Static localizer" = "Static localizer"
)

real_values_plot <- ggplot(svm_data, aes(x = ROI, y = Accuracy, fill = as.factor(Design))) +
  geom_bar(stat = "summary", fun = "mean", position = position_dodge(0.9), 
           alpha = 0.7, color = "black") +
  geom_jitter(
    aes(fill = as.factor(Design)),  
    position = position_jitterdodge(jitter.width = 0.5, dodge.width = 0.9),
    size = 2, alpha = 0.8, stroke = 0.5, shape = 21, color = "black"
  ) +
  geom_errorbar(
    stat = "summary",
    fun.data = mean_cl_normal,
    position = position_dodge(0.9),
    width = 0.4,
    size = 1.4,
    color = "black"
  ) +
  geom_errorbar(
    aes(color = as.factor(Design)),
    stat = "summary",
    fun.data = mean_cl_normal,
    position = position_dodge(0.9),
    width = 0.35,
    size = 0.7
  ) +
  geom_hline(yintercept = 0.5, linetype = "dotted", color = "red", size = 1) +
  scale_fill_grey(start = 0.9, end = 0.1, labels = design_labels) +
  scale_color_grey(start = 1, end = 1, guide = "none") +
  scale_x_discrete(labels = mask_labels) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
  coord_cartesian(ylim = c(0.0, 1.05)) +
  labs(
    title = "Decoding Accuracy by Mask and Design (95% CI) ",
    subtitle = "Within-Training Run Classification",
    x = "Mask",
    y = "Mean SVM Accuracy",
    fill = "Design"
  ) +
  theme_minimal() +
  theme(
    legend.position = "top",
    plot.title = element_text(size = 14, face = "bold", hjust=0),
    plot.subtitle = element_text(size = 12, face = "bold", hjust=0),
    axis.title.x = element_text(size = 12, face = "bold"),
    axis.title.y = element_text(size = 12, face = "bold"),
    axis.text.x = element_text(size = 12, angle = 45, hjust = 1, face = "bold"),
    axis.text.y = element_text(size = 12),
    legend.text = element_text(size = 12),
    legend.title = element_text(size = 12, face = "bold")
  )

print(real_values_plot)
ggsave(file.path(output_dir, "training_decoding_accuracy.tiff"), plot = real_values_plot, width = 8, height = 5, dpi = 300, device = "tiff")

# -------------------------------------------------
# Design pairwise comparisons (Wald, FDR corrected)
# -------------------------------------------------
design_comparisons <- emmeans(lmm_model, pairwise ~ Design | ROI, adjust = "none")
design_comparisons_table <- as.data.frame(summary(design_comparisons$contrasts, infer = c(TRUE, TRUE)))
design_comparisons_table$FDR_p_value <- p.adjust(design_comparisons_table$p.value, method = "fdr")

design_comparisons_table <- design_comparisons_table %>%
  transmute(
    ROI = ROI,
    Estimate = round(estimate, 2),
    CI_Lower = round(asymp.LCL, 2),
    CI_Upper = round(asymp.UCL, 2),
    `z-value` = round(z.ratio, 2),
    `p-value` = case_when(
      p.value < 0.001 ~ "<.001",
      TRUE ~ sprintf("%.3f", p.value)
    ),
    `FDR p-value` = case_when(
      FDR_p_value < 0.001 ~ "<.001",
      TRUE ~ sprintf("%.3f", FDR_p_value)
    ),
    `p-value (FDR)` = paste0(`p-value`, " (", `FDR p-value`, ")")
  )

print(design_comparisons_table)
write.csv(design_comparisons_table, file.path(output_dir, "training_design_pairwise_comparisons_Wald_FDR.csv"), row.names = FALSE)
