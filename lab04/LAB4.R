multiplicative_congruential <- function(n, a = 2^32+3, m = 2^63, seed = 12345) {
  x <- numeric(n)
  x[1] <- seed
  for (i in 2:n) {
    x[i] <- (a * x[i-1]) %% m
  }
  return(x / m)
}

set.seed(12345)
n <- 100000

my_rng_values <- multiplicative_congruential(n)
r_builtin_values <- runif(n)

my_mean <- mean(my_rng_values)
my_var <- var(my_rng_values)

r_mean <- mean(r_builtin_values)
r_var <- var(r_builtin_values)

theoretical_mean <- 0.5
theoretical_var <- 1/12

results <- data.frame(
  Генератор = c("Реализованный", "Встроенный", "Теоретический"),
  Среднее = c(my_mean, r_mean, theoretical_mean),
  Дисперсия = c(my_var, r_var, theoretical_var)
)

comparison <- data.frame(
  Генератор = c("Реализованный", "Встроенный"),
  среднее = c(my_mean/theoretical_mean, r_mean/theoretical_mean),
  дисперсия = c(my_var/theoretical_var, r_var/theoretical_var)
)

print(results)
print(comparison)