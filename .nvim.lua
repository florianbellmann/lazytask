require("overseer").register_template({
	name = "Run lazytask",
	params = {},
	condition = {
		dir = vim.fn.getcwd(),
	},
	builder = function()
		return {
			cmd = { "go" },
			args = { "run", "main.go" },
		}
	end,
})
require("overseer").register_template({
	name = "Test lazytask",
	params = {},
	condition = {
		dir = vim.fn.getcwd(),
	},
	builder = function()
		return {
			cmd = { "go" },
			args = { "test", "./..." },
		}
	end,
})
require("overseer").register_template({
	name = "Lint lazytask",
	params = {},
	condition = {
		dir = vim.fn.getcwd(),
	},
	builder = function()
		return {
			cmd = { "golangci-lint" },
			args = { "run" },
		}
	end,
})
